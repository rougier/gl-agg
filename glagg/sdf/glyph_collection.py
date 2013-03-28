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
import math
import numpy as np
import OpenGL.GL as gl
from glagg.shader import Shader
from glagg.collection import Collection
from glagg.transforms import orthographic
from glagg.sdf.font_manager import FontManager


# -----------------------------------------------------------------------------
class GlyphCollection(Collection):
    ''' '''

    def __init__(self, font_manager=None):
        
        self.vtype = np.dtype( [('a_position', 'f4', 2),
                                ('a_texcoord', 'f4', 2)] )
        self.utype = np.dtype( [('color',      'f4', 4),
                                ('translate',  'f4', 2),
                                ('scale',      'f4', 1),
                                ('rotate',     'f4', 1)] )
        self.font_manager = font_manager
        Collection.__init__(self, self.vtype, self.utype)
        shaders = os.path.join(os.path.dirname(__file__),'../shaders')
        vertex_shader= os.path.join( shaders, 'sdf_text.vert')
        fragment_shader= os.path.join( shaders, 'sdf_text.frag')
        self.shader = Shader( open(vertex_shader).read(),
                              open(fragment_shader).read() )


    # ---------------------------------
    def bounding_box(self, text, family='Sans', size=16, bold=False, italic=False, tight=False):
        prev = None
        width, height = 0,0
        descender, ascender = 0,0
        for i,charcode in enumerate(text):
            glyph = font[charcode]
            kerning = glyph.get_kerning(prev)
            y0 = glyph.offset[1]
            y1 = y0 - glyph.size[1]
            ascender = max(ascender,y0)
            descender = min(ascender,y1)
            width += glyph.advance[0]/64.0 + kerning
            height = max(height, glyph.size[1])
            prev = charcode
        if tight:
            width = width - glyph.advance[0] - kerning + glyph.size[0]
            height = height
        else:
           width = width
           height = font.height
           ascender = font.ascender
           descender = font.descender

        return width, height, ascender, descender
        

    # ---------------------------------
    def append( self, text,
                family='Sans', size=16, bold=False, italic=False,
                color=(0.0, 0.0, 0.0, 1.0),
                translate=(0,0), scale = 1.0, rotate = 0.0, tight_bbox=True,
                anchor_x='left', anchor_y='baseline', filename='./Vera.ttf'):

        filename = os.path.join('.', 'Vera.ttf')
        font = self.font_manager.get(filename, size)
        n = len(text)
        V = self.bake(text, font, anchor_x, anchor_y, tight_bbox=True)
        I = np.resize( np.array([0,1,2,0,2,3], dtype=np.uint32), n*(2*3))
        I += np.repeat( 4*np.arange(n), 6)
        U = np.zeros(1, self.utype)
        U['color']       = color
        U['translate']   = translate
        U['scale']       = scale
        U['rotate']      = rotate
        Collection.append(self,V,I,U)


    # ---------------------------------
    def bake(self, text, font, anchor_x='center', anchor_y='center', tight_bbox=True):
        vertices = np.zeros( len(text)*4, dtype = self.vtype )
        prev = None
        x,y = 0, 0
        width, height = 0,0
        linewidth, lineheight = 0,0
        descender, ascender = 0,0
        for i,charcode in enumerate(text):

            if charcode == '\n':
                width = max(linewidth, width)
                height = max(lineheight, height)
                x = 0
                y -= lineheight
                linewidth, lineheight = 0,0
                continue

            glyph = font[charcode]
            kerning = glyph.get_kerning(prev)
            x0 = x + glyph.offset[0] + kerning
            y0 = y + glyph.offset[1]
            x1 = x0 + glyph.size[0]
            y1 = y0 - glyph.size[1]

            y0 = int(y0)
            y1 = int(y1)
            x0 = int(x0)
            x1 = int(x1)

            u0 = glyph.texcoords[0]
            v0 = glyph.texcoords[1]
            u1 = glyph.texcoords[2]
            v1 = glyph.texcoords[3]
            index     = i*4
            indices   = [index, index+1, index+2, index, index+2, index+3]
            position  = [[x0,y0],[x0,y1],[x1,y1], [x1,y0]]
            texcoords = [[u0,v0],[u0,v1],[u1,v1], [u1,v0]]

            vertices['a_position'][i*4:i*4+4] = position
            vertices['a_texcoord'][i*4:i*4+4] = texcoords
            x += glyph.advance[0] + kerning
            y += glyph.advance[1]

            ascender = max(ascender,y0)
            descender = min(ascender,y1)
            linewidth += glyph.advance[0] + kerning
            lineheight = max(height, glyph.size[1])
            prev = charcode

        # Tight bounding box
        if tight_bbox:
            width = width - glyph.advance[0] - kerning + glyph.size[0]
            height = height
        # Loose bounding box
        else:
           width = width
           height = font.height
           ascender = font.ascender
           descender = font.descender

        if anchor_y == 'top':
            dy = -round(ascender)
        elif anchor_y == 'center':
            dy = -round(height/2+descender)
        elif anchor_y == 'bottom':
            dy = -round(descender)
        else:
            dy = 0
        if anchor_x == 'right':
            dx = -width/1.0
        elif anchor_x == 'center':
            dx = -width/2.0
        else:
            dx = 0
        vertices['a_position'] += round(dx), round(dy)

        return vertices

    # ---------------------------------
    def draw(self, P=None, V=None, M=None):
        manager = self.font_manager
        atlas = manager.atlas
        shader = self.shader

        if self._dirty:
            self.upload()

        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glEnable(gl.GL_BLEND)
        _,_,width,height = gl.glGetIntegerv( gl.GL_VIEWPORT )
        P = orthographic( 0, width, 0, height, -1, +1 )
        V = np.eye(4).astype( np.float32 )
        M = np.eye(4).astype( np.float32 )

        shader.bind()

        gl.glActiveTexture( gl.GL_TEXTURE0 )
        shader.uniformi( 'u_uniforms', 0 )
        gl.glBindTexture( gl.GL_TEXTURE_2D, self._ubuffer_id )
        shape = self._ubuffer_shape
        shader.uniformf( 'u_uniforms_shape', shape[1]//4, shape[0])

        gl.glActiveTexture( gl.GL_TEXTURE1 )
        shader.uniformi( 'u_font_atlas', 1 )
        gl.glBindTexture( gl.GL_TEXTURE_2D, manager.atlas_texture.id)
        shader.uniformf( 'u_font_atlas_shape',
                         manager.atlas.width, manager.atlas.height)
        
        gl.glActiveTexture( gl.GL_TEXTURE2 )
        shader.uniformi( 'u_filter_lut', 2 )
        gl.glBindTexture( gl.GL_TEXTURE_1D, manager.filter_texture.id)

        shader.uniform_matrixf( 'u_M', M )
        shader.uniform_matrixf( 'u_V', V )
        shader.uniform_matrixf( 'u_P', P )
        gl.glDisable( gl.GL_DEPTH_TEST )
        self._vbuffer.draw( )
        shader.unbind()
