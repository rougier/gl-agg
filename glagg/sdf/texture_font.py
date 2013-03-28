#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# glumpy is an OpenGL framework for the fast visualization of numpy arrays.
# Copyright (C) 2009-2011  Nicolas P. Rougier. All rights reserved.
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
import sys
import numpy as np
from freetype import *
import OpenGL.GL as gl
import OpenGL.GLUT as glut
from scipy.ndimage.interpolation import zoom

from glagg.transforms import *
from glagg.shader import Shader
from glagg.sdf.sdf import compute_sdf
from glagg.vertex_buffer import VertexBuffer


# -----------------------------------------------------------------------------
class TextureGlyph:
    '''
    A glyph gathers information relative to the size/offset/advance and texture
    coordinates of a single character. It is generally built automatically by a
    Font.
    '''

    def __init__(self, charcode, size, offset, advance, texcoords):
        '''
        Build a new texture glyph

        Parameter:
        ----------

        charcode : char
            Represented character

        size: tuple of 2 ints
            Glyph size in pixels

        offset: tuple of 2 floats
            Glyph offset relatively to anchor point

        advance: tuple of 2 floats
            Glyph advance

        texcoords: tuple of 4 floats
            Texture coordinates of bottom-left and top-right corner
        '''
        self.charcode = charcode
        self.size = size
        self.offset = offset
        self.advance = advance
        self.texcoords = texcoords
        self.kerning = {}


    def get_kerning(self, charcode):
        ''' Get kerning information

        Parameters:
        -----------

        charcode: char
            Character preceding this glyph
        '''
        if charcode in self.kerning.keys():
            return self.kerning[charcode]
        else:
            return 0


# -----------------------------------------------------------------------------
class TextureFont:
    def __init__(self, filename, atlas):
        self.atlas = atlas
        self.filename = filename
        self.glyphs = {}
        face = Face( self.filename )
        face.set_char_size( int(64*64))
        metrics = face.size
        self.ascender  = metrics.ascender/64.0
        self.descender = metrics.descender/64.0
        self.height    = metrics.height/64.0
        self.linegap   = self.height - self.ascender + self.descender

    def __getitem__(self, charcode):
        if charcode not in self.glyphs.keys():
            self.load('%c' % charcode)
        return self.glyphs[charcode]

    def load_glyph(self, face, charcode, h_size=512, l_size=64, padding=0.25):
        face.set_char_size( h_size*64 )
        face.load_char(charcode, FT_LOAD_RENDER | FT_LOAD_NO_HINTING | FT_LOAD_NO_AUTOHINT);

        bitmap = face.glyph.bitmap
        width  = face.glyph.bitmap.width
        height = face.glyph.bitmap.rows
        pitch  = face.glyph.bitmap.pitch

        # Get glyph into a numpy array
        G = np.array(bitmap.buffer).reshape(height,pitch)
        G = G[:,:width].astype(np.ubyte)

        # Pad high resolution glyph with a blank border and normalize values
        # between 0 and 1
        h_width  = (1+2*padding)*width
        h_height = (1+2*padding)*height
        h_data = np.zeros( (h_height,h_width), np.double)
        ox,oy = padding*width, padding*height
        h_data[oy:oy+height, ox:ox+width] = G/255.0

       # Compute distance field at high resolution
        compute_sdf(h_data)

       # Scale down glyph to low resoltion size
        ratio = l_size/float(h_size)
        l_data = 1 - zoom(h_data, ratio, cval=1.0)

       # Compute information at low resolution size
        size   = ( l_data.shape[1],l_data.shape[0] )
        offset = ( (face.glyph.bitmap_left - padding*width) * ratio,
                   (face.glyph.bitmap_top + padding*height) * ratio )
        advance = ( (face.glyph.advance.x/64.0)*ratio,
                    (face.glyph.advance.y/64.0)*ratio )
        return l_data, size, offset, advance


    def load(self, charcodes = ''):
        face = Face( self.filename )

        for charcode in charcodes:
            if charcode in self.glyphs.keys():
                continue
            self.atlas._dirty = True
            data,size,offset,advance = self.load_glyph(face, charcode, 256, 64)
            w,h = size
            x,y = self.atlas.allocate(w+2,h+2)
            self.atlas.add(data, (x+1,y+1,w,h))
            x += 1
            y += 1

            u0     = (x +     0.0)/float(self.atlas.width)
            v0     = (y +     0.0)/float(self.atlas.height)
            u1     = (x + w - 0.0)/float(self.atlas.width)
            v1     = (y + h - 0.0)/float(self.atlas.height)
            texcoords = (u0,v0,u1,v1)
            glyph = TextureGlyph(charcode, size, offset, advance, texcoords)
            self.glyphs[charcode] = glyph
            # Generate kerning
            face.set_char_size( 64*64 )
            for g in self.glyphs.values():
                kerning = face.get_kerning(g.charcode, charcode, mode=FT_KERNING_UNFITTED)
                if kerning.x != 0:
                    glyph.kerning[g.charcode] = kerning.x/64.0
                kerning = face.get_kerning(charcode, g.charcode, mode=FT_KERNING_UNFITTED)
                if kerning.x != 0:
                    g.kerning[charcode] = kerning.x/64.0
