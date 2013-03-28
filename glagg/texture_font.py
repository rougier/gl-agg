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
import os
import numpy as np
from freetype import *


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
    '''
    A Font gathers a set of glyph relatively to a given font filename
    and size.
    '''

    def __init__(self, filename, size, atlas):
        '''
        Initialize font

        Parameters:
        -----------

        atlas: Atlas
            Atlas where glyph will be stored

        filename: str
            Font filename
        
        size : float
            Font size
        '''

        self.atlas = atlas
        self.filename = filename
        self.size = size
        self.glyphs = {}
        face = Face( self.filename )
        face.set_char_size( int(self.size*64))
        metrics = face.size
        self.ascender  = metrics.ascender/64.0
        self.descender = metrics.descender/64.0
        self.height    = metrics.height/64.0
        self.linegap   = self.height - self.ascender + self.descender
        self.depth     = self.atlas.depth
        set_lcd_filter(FT_LCD_FILTER_LIGHT)


    def __getitem__(self, charcode):
        '''
        x.__getitem__(y) <==> x[y]
        '''
        if charcode not in self.glyphs.keys():
            self.load('%c' % charcode)
        return self.glyphs[charcode]


 
    def load(self, charcodes = ''):
        '''
        Build glyphs corresponding to individual characters in charcodes.

        Parameters:
        -----------
        
        charcodes: [str | unicode]
            Set of characters to be represented
        '''
        face = Face( self.filename )
        pen = Vector(0,0)
        hres = 64
        hscale = 1.0/64
        face.set_char_size( int(self.size * 64), 0, hres*72, 72 )
        matrix = Matrix( int((hscale) * 0x10000L), int((0.0) * 0x10000L),
                         int((0.0)    * 0x10000L), int((1.0) * 0x10000L) )

        for charcode in charcodes:
            face.set_transform( matrix, pen )
            if charcode in self.glyphs.keys():
                continue
            self.atlas._dirty = True
            flags = FT_LOAD_RENDER | FT_LOAD_FORCE_AUTOHINT
            if self.depth == 3:
                flags |= FT_LOAD_TARGET_LCD

            face.load_char( charcode, flags )
            bitmap = face.glyph.bitmap
            left   = face.glyph.bitmap_left
            top    = face.glyph.bitmap_top
            width  = face.glyph.bitmap.width
            rows   = face.glyph.bitmap.rows
            pitch  = face.glyph.bitmap.pitch


            x,y,w,h = self.atlas.get_region(width/self.depth+2, rows+2)
            if x < 0:
                print 'Missed !'
                continue
            x,y = x+1, y+1
            w,h = w-2, h-2
            data = np.array(bitmap.buffer).reshape(rows,pitch)
            data = (data[:,:width].astype(np.ubyte))
            data = data.reshape(rows,width/self.depth,self.depth)
            self.atlas.set_region((x,y,w,h), data)

            # Build glyph
            size   = w,h
            offset = left, top
            advance= face.glyph.advance.x, face.glyph.advance.y

            u0     = (x +     0.0)/float(self.atlas.width)
            v0     = (y +     0.0)/float(self.atlas.height)
            u1     = (x + w - 0.0)/float(self.atlas.width)
            v1     = (y + h - 0.0)/float(self.atlas.height)
            texcoords = (u0,v0,u1,v1)
            glyph = TextureGlyph(charcode, size, offset, advance, texcoords)
            self.glyphs[charcode] = glyph

            # Generate kerning
            for g in self.glyphs.values():
                # 64 * 64 because of 26.6 encoding AND the transform matrix used
                # in texture_font_load_face (hres = 64)
                kerning = face.get_kerning(g.charcode, charcode, mode=FT_KERNING_UNFITTED)
                if kerning.x != 0:
                    glyph.kerning[g.charcode] = kerning.x/(64.0*hres)
                kerning = face.get_kerning(charcode, g.charcode, mode=FT_KERNING_UNFITTED)
                if kerning.x != 0:
                    g.kerning[charcode] = kerning.x/(64.0*hres)
            # High resolution advance.x calculation
            # gindex = face.get_char_index( charcode )
            # a = face.get_advance(gindex, FT_LOAD_RENDER | FT_LOAD_TARGET_LCD)/(64*72)
            # glyph.advance = a, glyph.advance[1]
