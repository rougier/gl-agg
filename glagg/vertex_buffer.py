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
import ctypes
import numpy as np
import OpenGL.GL as gl
from dynamic_buffer import DynamicBuffer


# -----------------------------------------------------------------------------
class VertexAttributeException(Exception):
    pass



# -----------------------------------------------------------------------------
class VertexAttribute(object):

    def __init__(self, name, count, gltype, stride, offset, normalized=False):
        self.index  = -1
        self.name   = name
        self.count  = count
        self.gltype = gltype
        self.stride = stride
        self.offset = ctypes.c_void_p(offset)
        self.normalized = normalized

    def enable(self):
        if self.index == -1:
            program = gl.glGetIntegerv( gl.GL_CURRENT_PROGRAM )
            if not program:
                return
            self.index = gl.glGetAttribLocation( program, self.name )
            if self.index == -1:
                return
        gl.glEnableVertexAttribArray( self.index )
        gl.glVertexAttribPointer( self.index, self.count, self.gltype,
                                  self.normalized, self.stride, self.offset )




# -----------------------------------------------------------------------------
class VertexBufferException(Exception):
    pass



# -----------------------------------------------------------------------------
class VertexBuffer(object):

    # ---------------------------------
    def __init__(self, dtype):
        # Parse vertices dtype and generate attributes
        gltypes = { 'float32': gl.GL_FLOAT,
                    'float'  : gl.GL_DOUBLE, 'float64': gl.GL_DOUBLE,
                    'int8'   : gl.GL_BYTE,   'uint8'  : gl.GL_UNSIGNED_BYTE,
                    'int16'  : gl.GL_SHORT,  'uint16' : gl.GL_UNSIGNED_SHORT,
                    'int32'  : gl.GL_INT,    'uint32' : gl.GL_UNSIGNED_INT }
        dtype = np.dtype(dtype)
        names = dtype.names or []
        stride = dtype.itemsize
        offset = 0
        self._attributes = []
        for i,name in enumerate(names):
            if dtype[name].subdtype is not None:
                gtype = str(dtype[name].subdtype[0])
                count = reduce(lambda x,y:x*y, dtype[name].shape)
            else:
                gtype = str(dtype[name])
                count = 1
            if gtype not in gltypes.keys():
                raise VertexBufferException('Data type not understood')
            gltype = gltypes[gtype]
            attribute = VertexAttribute(name,count,gltype,stride,offset)
            self._attributes.append( attribute )
            offset += dtype[name].itemsize

        self._vertices = DynamicBuffer(dtype)
        self._indices  = DynamicBuffer(np.uint32)
        self._vertices_id = 0
        self._indices_id = 0
        self._dirty = True


    # ---------------------------------
    def get_vertices(self):
        return self._vertices.data
    vertices = property(get_vertices)


    # ---------------------------------
    def get_indices(self):
        return self._indices.data
    indices = property(get_indices)


    # ---------------------------------
    def clear(self):
        self._vertices.clear()
        self._indices.clear()
        self._dirty = True


    # ---------------------------------
    def append(self, vertices, indices):
        vsize = len(self._vertices.data)
        vertices = np.array(vertices).astype(self._vertices.dtype)
        self._vertices.append(vertices)
        indices = np.array(indices).astype(self._indices.dtype) + vsize
        self._indices.append(indices)
        self._dirty = True


    # ---------------------------------
    def __delitem__(self, key):
        vsize = len(self._vertices[key])
        _,_,dstart,_ = self._indices._get_indices(key)
        del self._vertices[key]
        del self._indices[key]
        self._indices.data[dstart:] -= vsize
        self._dirty = True


    # ---------------------------------
    def __getitem__(self, key):
        return self._vertices[key], self._indices[key]


    # ---------------------------------
    def __len__(self):
        return len(self.vertices)


    # ---------------------------------
    def upload(self):

        if not self._dirty:
            return

        if not self._vertices_id:
            self._vertices_id = gl.glGenBuffers(1)
        gl.glBindBuffer( gl.GL_ARRAY_BUFFER, self._vertices_id )
        gl.glBufferData( gl.GL_ARRAY_BUFFER, self._vertices.data, gl.GL_DYNAMIC_DRAW )
        gl.glBindBuffer( gl.GL_ARRAY_BUFFER, 0 )

        if not self._indices_id:
            self._indices_id = gl.glGenBuffers(1)
        gl.glBindBuffer( gl.GL_ELEMENT_ARRAY_BUFFER, self._indices_id )
        gl.glBufferData( gl.GL_ELEMENT_ARRAY_BUFFER, self._indices.data, gl.GL_DYNAMIC_DRAW )
        gl.glBindBuffer( gl.GL_ELEMENT_ARRAY_BUFFER, 0 )

        self._dirty = False


    # ---------------------------------
    def draw( self, mode=gl.GL_TRIANGLES ):

        if self._dirty:
            self.upload()
        gl.glBindBuffer( gl.GL_ARRAY_BUFFER, self._vertices_id )
        gl.glBindBuffer( gl.GL_ELEMENT_ARRAY_BUFFER, self._indices_id )
        for attribute in self._attributes:
            attribute.enable()
        gl.glDrawElements( mode, len(self._indices.data), gl.GL_UNSIGNED_INT, None)
        gl.glBindBuffer( gl.GL_ELEMENT_ARRAY_BUFFER, 0 )
        gl.glBindBuffer( gl.GL_ARRAY_BUFFER, 0 )



# -----------------------------------------------------------------------------
if __name__ == '__main__':
    buffer = VertexBuffer( float )
    buffer.append ([1.0,1.0],         [0,1])
    buffer.append ([2.0,2.0,2.0,2.0], [0,1,2,3])
    buffer.append ([3.0,3.0,3.0,3.0], [0,1,2,3])
    buffer.append ([4.0,4.0],         [0,1])
    buffer.append ([5.0,5.0,5.0,5.0], [3,2,1,0])
    buffer.append ([1.0,1.0],         [0,1])

    print buffer.vertices
    print buffer.indices
    del buffer[:-1]
    print buffer.vertices
    print buffer.indices
