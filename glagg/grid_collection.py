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
import os
import numpy as np
import OpenGL.GL as gl
from shader import Shader
from dash_atlas import DashAtlas
from collection import Collection
from transforms import orthographic
from dynamic_buffer import DynamicBuffer


# -----------------------------------------------------------------------------
class GridCollection(Collection):

    # ---------------------------------
    def __init__(self, dash_atlas = None):
        self.vtype = np.dtype( [('a_texcoord', 'f4', 2)] )
        self.utype = np.dtype( [('translate',        'f4', 2),
                                ('scale',            'f4', 1),
                                ('rotate',           'f4', 1),
                                ('major_grid',       'f4', 2),
                                ('minor_grid',       'f4', 2),
                                ('major_tick_size',  'f4', 2),
                                ('minor_tick_size',  'f4', 2),
                                ('major_grid_color', 'f4', 4),
                                ('minor_grid_color', 'f4', 4),
                                ('major_tick_color', 'f4', 4),
                                ('minor_tick_color', 'f4', 4),
                                ('major_grid_width', 'f4', 1),
                                ('minor_grid_width', 'f4', 1),
                                ('major_tick_width', 'f4', 1),
                                ('minor_tick_width', 'f4', 1),
                                ('size',             'f4', 2),
                                ('offset',           'f4', 2),
                                ('zoom',             'f4', 1),
                                ('antialias',        'f4', 1),
                                ('major_dash_phase', 'f4', 1),
                                ('minor_dash_phase', 'f4', 1),
                                ('major_dash_index', 'f4', 1),
                                ('major_dash_period','f4', 1),
                                ('major_dash_caps',  'f4', 2),
                                ('minor_dash_period','f4', 1),
                                ('minor_dash_index', 'f4', 1),
                                ('minor_dash_caps',  'f4', 2)
                                ] )
        self.gtype = np.dtype( [('name', 'f4', (1024,4))] )
        Collection.__init__(self, self.vtype, self.utype)
        if dash_atlas is None:
            self.dash_atlas = DashAtlas()
        else:
            self.dash_atlas = dash_atlas
        shaders = os.path.join(os.path.dirname(__file__),'shaders')
        vertex_shader= os.path.join( shaders, 'grid.vert')
        fragment_shader= os.path.join( shaders, 'grid.frag')
        self.shader = Shader( open(vertex_shader).read(),
                              open(fragment_shader).read() )
        self._gbuffer = DynamicBuffer( self.gtype )
        self._gbuffer_shape = [0,4*1024]
        self._gbuffer_id = 0


    # ---------------------------------
    def append( self, size = (1,1), antialias = 1.0,
                translate = (0,0), scale = 1.0, rotate = 0.0,
                offset = (0,0), zoom = 1,
                major_grid = [64.,64.], minor_grid = [8.,8.],
                major_grid_color = np.array([0.0, 0.0, 0.0, 0.75]),
                minor_grid_color = np.array([0.0, 0.0, 0.0, 0.25]),
                major_tick_color = np.array([0.0, 0.0, 0.0, 1.0]),
                minor_tick_color = np.array([0.0, 0.0, 0.0, 1.0]),
                major_grid_width = 1.0,
                minor_grid_width = 1.0,
                major_tick_size = np.array([10.0,10.0]),
                minor_tick_size = np.array([ 5.0, 5.0]),
                major_tick_width = 1.5,
                minor_tick_width = 1.00,
                major_dash_pattern='dotted',
                major_dash_phase = 0.0,
                major_dash_caps = ('round','round'),
                minor_dash_pattern='dotted',
                minor_dash_phase = 0.0,
                minor_dash_caps = ('round','round') ):

        V, I, _ = self.bake()
        U = np.zeros(1, self.utype)
        U['translate']        = translate
        U['scale']            = scale
        U['rotate']           = rotate 
        U['major_grid']       = major_grid
        U['minor_grid']       = minor_grid
        U['major_tick_size']  = major_tick_size
        U['minor_tick_size']  = minor_tick_size
        U['major_grid_color'] = major_grid_color
        U['minor_grid_color'] = minor_grid_color
        U['major_tick_color'] = major_tick_color
        U['minor_tick_color'] = minor_tick_color
        U['major_grid_width'] = major_grid_width
        U['minor_grid_width'] = minor_grid_width
        U['major_tick_width'] = major_tick_width
        U['minor_tick_width'] = minor_tick_width
        U['size']             = size
        U['offset']           = offset
        U['zoom']             = zoom
        U['antialias']        = antialias 

        if self.dash_atlas:
            dash_index, dash_period = self.dash_atlas[major_dash_pattern]
            U['major_dash_phase']  = major_dash_phase
            U['major_dash_index']  = dash_index
            U['major_dash_period'] = dash_period
            U['major_dash_caps']   = ( self.caps.get(major_dash_caps[0], 'round'),
                                       self.caps.get(major_dash_caps[1], 'round') )

            dash_index, dash_period = self.dash_atlas[minor_dash_pattern]
            U['minor_dash_phase']  = minor_dash_phase
            U['minor_dash_index']  = dash_index
            U['minor_dash_period'] = dash_period
            U['minor_dash_caps']   = ( self.caps.get(minor_dash_caps[0], 'round'),
                                       self.caps.get(minor_dash_caps[1], 'round') )


        Collection.append(self,V,I,U)
        G = np.empty((1024,4), dtype='f4')
        G = G.ravel().view(self.gtype)
        self._gbuffer.append(G)
        index = len(self._gbuffer)
        self._gbuffer_shape = [index,4*1024]
        self.update_gbuffer(index-1)

    # ---------------------------------
    def set_major_grid(self, key, major_grid):
        self._ubuffer.data[key]['major_grid'][...] = major_grid
        self.update_gbuffer(key)

    # ---------------------------------
    def set_minor_grid(self, key, minor_grid):
        self._ubuffer.data[key]['minor_grid'][...] = minor_grid
        self.update_gbuffer(key)

    # ---------------------------------
    def set_zoom(self, key, zoom):
        self._ubuffer.data[key]['zoom'] = zoom
        self.update_gbuffer(key)

    # ---------------------------------
    def set_offset(self, key, offset):
        self._ubuffer.data[key]['offset'][...] = offset
        self.update_gbuffer(key)

    # ---------------------------------
    def set_size(self, key, size):
        self._ubuffer.data[key]['size'][...] = size
        self.update_gbuffer(key)

    # ---------------------------------
    def update_gbuffer(self, key):

        def find_closest(A, target):
            # A must be sorted
            idx = A.searchsorted(target)
            idx = np.clip(idx, 1, len(A)-1)
            left = A[idx-1]
            right = A[idx]
            idx -= target - left < right - target
            return idx

        major_grid = self._ubuffer.data[key]['major_grid']
        minor_grid = self._ubuffer.data[key]['minor_grid']
        zoom       = self._ubuffer.data[key]['zoom']
        offset     = self._ubuffer.data[key]['offset']
        w,h        = self._ubuffer.data[key]['size']
        n = 1024

        t1 = major_grid[0]*zoom
        t2 = minor_grid[0]*zoom
        t3 = major_grid[1]*zoom
        t4 = minor_grid[1]*zoom

        I1 = np.arange(np.fmod(offset[0],t1), np.fmod(offset[0],t1)+w+t1,t1)
        I2 = np.arange(np.fmod(offset[0],t2), np.fmod(offset[0],t2)+w+t2,t2)
        I3 = np.arange(np.fmod(offset[1],t3), np.fmod(offset[1],t3)+h+t3,t3)
        I4 = np.arange(np.fmod(offset[1],t4), np.fmod(offset[1],t4)+h+t4,t4)

        # I1 = np.logspace(np.log10(1), np.log10(2*w), 5)*zoom        
        # I2 = np.logspace(np.log10(1), np.log10(2*w), 50)*zoom
        # I3 = np.logspace(np.log10(1), np.log10(2*h), 5)*zoom
        # I4 = np.logspace(np.log10(1), np.log10(2*h), 50)*zoom

        # We are here in screen space and we want integer coordinates
        np.floor(I1,out=I1)
        np.floor(I2,out=I2)
        np.floor(I3,out=I3)
        np.floor(I4,out=I4)
        L = np.linspace(0,w,n)
        G = np.empty((1024,4), dtype='f4')
        G[:,0] = I1[find_closest(I1,L)]
        G[:,2] = I2[find_closest(I2,L)]
        L = np.linspace(0,h,n)
        G[:,1] = I3[find_closest(I3,L)]
        G[:,3] = I4[find_closest(I4,L)]
        G = G.ravel().view(self.gtype)
        self._gbuffer[key] = G
        self._dirty = True


    # ---------------------------------
    def bake(self):
        V = np.zeros( 4, dtype = self.vtype )
        V['a_texcoord'] = (0,0),(0,1), (1,0),(1,1) 
        I = np.array([0,1,2,1,2,3],dtype=np.int32)
        return V, I, 0


    # ---------------------------------
    def upload(self):
        if not self._dirty:
            return

        Collection.upload( self )

        gl.glActiveTexture( gl.GL_TEXTURE2 )
        data = self._gbuffer.data.view(np.float32)
        shape = len(self._gbuffer), 4*1024
        if not self._gbuffer_id:
            self._gbuffer_id = gl.glGenTextures(1)

            gl.glBindTexture( gl.GL_TEXTURE_2D, self._gbuffer_id )
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
            gl.glTexImage2D( gl.GL_TEXTURE_2D, 0, gl.GL_RGBA32F,
                             shape[1]//4, shape[0], 0, gl.GL_RGBA, gl.GL_FLOAT, data )

        gl.glActiveTexture( gl.GL_TEXTURE2 )
        gl.glBindTexture( gl.GL_TEXTURE_2D, self._gbuffer_id )
        gl.glTexImage2D( gl.GL_TEXTURE_2D, 0, gl.GL_RGBA32F,
                         shape[1]//4, shape[0], 0, gl.GL_RGBA, gl.GL_FLOAT, data )
        self._dirty = False

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
        shape = self._ubuffer_shape
        shader.uniformf( 'u_uniforms_shape', shape[1]//4, shape[0])
        gl.glBindTexture( gl.GL_TEXTURE_2D, self._ubuffer_id )

        if self.dash_atlas:
            gl.glActiveTexture( gl.GL_TEXTURE1 )
            shader.uniformi('u_dash_atlas', 1)
            gl.glBindTexture( gl.GL_TEXTURE_2D, self.dash_atlas.texture_id )

        gl.glActiveTexture( gl.GL_TEXTURE2 )
        gl.glBindTexture( gl.GL_TEXTURE_2D, self._gbuffer_id )
        shader.uniformi( 'u_gbuffer', 2 )
        shape = self._gbuffer_shape
        shader.uniformf( 'u_gbuffer_shape', shape[1]//4, shape[0])

        shader.uniform_matrixf( 'u_M', M )
        shader.uniform_matrixf( 'u_V', V )
        shader.uniform_matrixf( 'u_P', P )
        self._vbuffer.draw( )
        shader.unbind()
