#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (C) 2013 Nicolas P. Rougier. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY NICOLAS P. ROUGIER ''AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL NICOLAS P. ROUGIER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of Nicolas P. Rougier.
# -----------------------------------------------------------------------------
"""
A collection is a container for several objects having the same vertex
structure (vtype) and same uniforms type (utype). A collection allows to
manipulate objects individually but they can be rendered at once (single call).

Each object can have its own set of uniforms provided they are a combination of
floats.
"""
import numpy as np
import OpenGL
import OpenGL.GL as gl
from operator import mul

from transforms import orthographic
from vertex_buffer import VertexBuffer
from dynamic_buffer import DynamicBuffer


# -----------------------------------------------------------------------------
def dtype_reduce(dtype, level=0, depth=0):
    """
    Try to reduce dtype up to a given level when it is possible

    dtype =  [ ('vertex',  [('x', 'f4'), ('y', 'f4'), ('z', 'f4')]),
               ('normal',  [('x', 'f4'), ('y', 'f4'), ('z', 'f4')]),
               ('color',   [('r', 'f4'), ('g', 'f4'), ('b', 'f4'), ('a', 'f4')])]

    level 0: ['color,vertex,normal,', 10, 'float32']
    level 1: [['color', 4, 'float32']
              ['normal', 3, 'float32']
              ['vertex', 3, 'float32']]
    """
    dtype = np.dtype(dtype)
    fields = dtype.fields
    
    # No fields
    if fields is None:
        if dtype.shape:
            count = reduce(mul, dtype.shape)
        else:
            count = 1
        size = dtype.itemsize/count
        if dtype.subdtype:
            name = str( dtype.subdtype[0] )
        else:
            name = str( dtype )
        return ['', count, name]
    else:
        items = []
        name = ''
        # Get reduced fields
        for key,value in fields.items():
            l =  dtype_reduce(value[0], level, depth+1)
            if type(l[0]) is str:
                items.append( [key, l[1], l[2]] )
            else:
                items.append( l )
            name += key+','

        # Check if we can reduce item list
        ctype = None
        count = 0
        for i,item in enumerate(items):
            # One item is a list, we cannot reduce
            if type(item[0]) is not str:
                return items
            else:
                if i==0:
                    ctype = item[2]
                    count += item[1]
                else:
                    if item[2] != ctype:
                        return items
                    count += item[1]
        if depth >= level:
            return [name, count, ctype]
        else:
            return items



# -----------------------------------------------------------------------------
class Item(object):

    # ---------------------------------
    def __init__(self, parent, key, vertices, indices, uniforms):
        self.parent = parent
        self.vertices = vertices
        self.indices  = indices
        self.uniforms = uniforms
        self.key = key

    # ---------------------------------
    def __getitem__(self, key):
        if key in self.uniforms.dtype.names:
            return self.uniforms[key]
        raise KeyError

    # ---------------------------------
    def __setitem__(self, key, value):
        if key in self.uniforms.dtype.names:
            self.uniforms[key] = value
            self.parent._dirty = True
            return
        raise KeyError

    # ---------------------------------
    def __getattr__(self, name):
        if hasattr(self, 'uniforms'):
            uniforms = object.__getattribute__(self,'uniforms')
            if name in uniforms.dtype.names:
                return uniforms[name]
        return object.__getattribute__(self,name)

    # ---------------------------------
    def __setattr__(self, name, value):
        if hasattr(self, 'uniforms'):
            uniforms = object.__getattribute__(self,'uniforms')
            if name in uniforms.dtype.names:
                # Is there a method at the parent level ?
                if( hasattr(self.parent, 'set_'+name) ):
                    getattr(self.parent,'set_'+name)(self.key, value)
                    return
                uniforms[name] = value
                self.parent._dirty = True
                return
        object.__setattr__(self, name, value)



# -----------------------------------------------------------------------------
class CollectionException(Exception):
    pass



# -----------------------------------------------------------------------------
class Collection(object):

    join = { 'miter' : 0,
             'round' : 1,
             'bevel' : 2 }

    caps = { ''             : 0,
             'none'         : 0,
             '.'            : 0,
             'round'        : 1,
             ')'            : 1,
             '('            : 1,
             'o'            : 1,
             'triangle in'  : 2,
             '<'            : 2,
             'triangle out' : 3,
             '>'            : 3,
             'square'       : 4,
             '='            : 4,
             'butt'         : 4,
             '|'            : 5 }


    # ---------------------------------
    def __init__(self, vtype, utype):
        self.dash_atlas = None

        # Convert types to lists (in case they were already dtypes) such that
        # we can append new fields
        vtype = eval(str(np.dtype(vtype)))
        utype = eval(str(np.dtype(utype)))

        # We add a uniform index to access uniform data from texture
        vtype.append( ('a_index', 'f4') )

        # Check if given utype is made of float32 only
        rutype = dtype_reduce(utype)
        if type(rutype[0]) is not str or rutype[2] != 'float32':
            raise CollectionError("Uniform type cannot de reduced to float32 only")
        else:
            count = rutype[1]
            size = count//4
            if count % 4:
                size += 1
                utype.append(('unnused', 'f4', size*4-count))
            count = size*4
            self.utype = utype
        self._vbuffer = VertexBuffer(vtype)
        self._ubuffer = DynamicBuffer( utype ) 
        self._ubuffer_id = 0
        self._ubuffer_shape = [0,count]


    # ---------------------------------
    def __len__(self):
        return len(self._vbuffer)


    # ---------------------------------
    def __getitem__(self, key):
        V = self._vbuffer.vertices[key]
        I = self._vbuffer.indices[key]
        U = self._ubuffer[key]
        return Item(self, key, V, I, U)


    # ---------------------------------
    def __delitem__(self, key):
        start,end = self._vbuffer.vertices.range(key)
        del self._vbuffer[key]
        del self._ubuffer[key]
        self._vbuffer.vertices.data['a_index'][start:] -= 1
        self._vbuffer._dirty = True
        self._dirty = True


    # ---------------------------------
    def get_vertices(self):
        return self._vbuffer.vertices
    vertices = property(get_vertices)


    # ---------------------------------
    def get_indices(self):
        return self._vbuffer.indices
    indices = property(get_indices)


    # ---------------------------------
    def get_uniforms(self):
        return self._ubuffer
    uniforms = property(get_uniforms)


    # ---------------------------------
    def __getattr__(self, name):
        if hasattr(self, '_ubuffer'):
            buffer = object.__getattribute__(self,'_ubuffer')
            if name in buffer.dtype.names:
                return buffer.data[name]
        return object.__getattribute__(self,name)


    # ---------------------------------
    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        if hasattr(self, '_ubuffer'):
            buffer = object.__getattribute__(self,'_ubuffer')
            if name in buffer.dtype.names:
                buffer.data[name] = value
                # buffer._dirty = True
                object.__setattr__(self, '_dirty', True)
        object.__setattr__(self, name, value)


    # ---------------------------------
    def clear(self):
        self._vbuffer.clear()
        self._ubuffer.clear()
        self._dirty = True


    # ---------------------------------
    def append(self, vertices, indices, uniforms):
        vertices = np.array(vertices).astype(self._vbuffer.vertices.dtype)
        indices  = np.array(indices).astype(self._vbuffer.indices.dtype)
        uniforms = np.array(uniforms).astype(self._ubuffer.dtype)
        vertices['a_index'] = len(self)
        self._vbuffer.append( vertices, indices)
        self._ubuffer.append( uniforms )
        self._ubuffer_shape[0] = len(self)
        self._dirty = True


    # ---------------------------------
    def upload(self):

        if not self._dirty:
            return

        self._vbuffer.upload()

        gl.glActiveTexture( gl.GL_TEXTURE0 )
        data = self._ubuffer.data.view(np.float32)
        shape = self._ubuffer_shape
        if not self._ubuffer_id:
            self._ubuffer_id = gl.glGenTextures(1)

            gl.glBindTexture( gl.GL_TEXTURE_2D, self._ubuffer_id )
            gl.glPixelStorei( gl.GL_UNPACK_ALIGNMENT, 1 )
            gl.glPixelStorei( gl.GL_PACK_ALIGNMENT, 1 )
            gl.glTexParameterf( gl.GL_TEXTURE_2D,
                                gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST )
            gl.glTexParameterf( gl.GL_TEXTURE_2D,
                                gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST )
            gl.glTexParameterf( gl.GL_TEXTURE_2D,
                                gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE )
            gl.glTexParameterf( gl.GL_TEXTURE_2D,
                                gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE )
            gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_BASE_LEVEL, 0)
            gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAX_LEVEL, 0)
            gl.glTexImage2D( gl.GL_TEXTURE_2D, 0, gl.GL_RGBA32F_ARB,
                             shape[1]//4, shape[0], 0, gl.GL_RGBA, gl.GL_FLOAT, data )

        gl.glActiveTexture( gl.GL_TEXTURE0 )
        gl.glBindTexture( gl.GL_TEXTURE_2D, self._ubuffer_id )
        gl.glTexImage2D( gl.GL_TEXTURE_2D, 0, gl.GL_RGBA32F_ARB,
                         shape[1]//4, shape[0], 0, gl.GL_RGBA, gl.GL_FLOAT, data )
        #gl.glTexSubImage2D( gl.GL_TEXTURE_2D,0, 0, 0, shape[1]//4, shape[0],
        #                    gl.GL_RGBA, gl.GL_FLOAT, data);
        self._dirty = False


    # ---------------------------------
    def bake(self, vertices):
        raise NotImplemented


    # ---------------------------------
    def draw(self):
        if self._dirty:
            self.upload()

        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glEnable(gl.GL_BLEND)
        _,_,width,height = gl.glGetIntegerv( gl.GL_VIEWPORT )
        P = orthographic( 0, width, 0, height, -1, +1 )
        V = np.eye(4).astype( np.float32 )
        M = np.eye(4).astype( np.float32 )

        shader = self.shader
        shader.bind()
        gl.glActiveTexture( gl.GL_TEXTURE0 )
        shader.uniformi( 'u_uniforms', 0 )
        gl.glBindTexture( gl.GL_TEXTURE_2D, self._ubuffer_id )
        if self.dash_atlas:
            gl.glActiveTexture( gl.GL_TEXTURE1 )
            shader.uniformi('u_dash_atlas', 1)
            gl.glBindTexture( gl.GL_TEXTURE_2D, self.dash_atlas.texture_id )
        shader.uniform_matrixf( 'u_M', M )
        shader.uniform_matrixf( 'u_V', V )
        shader.uniform_matrixf( 'u_P', P )
        shape = self._ubuffer_shape
        shader.uniformf( 'u_uniforms_shape', shape[1]//4, shape[0])
        self._vbuffer.draw( )
        shader.unbind()
