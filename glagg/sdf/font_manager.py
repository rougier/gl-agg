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

#import glagg.spatial_filter
from glagg.texture import Texture
from glagg.atlas_buffer import AtlasBuffer
from glagg.sdf.texture_font import TextureFont


def _build_kernel(size=256):
    # From GPU Gems
    # Chapter 24. High-Quality Filtering
    # Kevin Bjorke, NVIDIA
    # http://http.developer.nvidia.com/GPUGems/gpugems_ch24.html
    #
    # Mitchell Netravali Reconstruction Filter
    # a = 1.0, b = 0.0  - cubic B-spline
    # B = 1/3, b = 1/3  - recommended
    # a = 0.5, b = 0.0  - Catmull-Rom spline
    def MitchellNetravali(x, a=1, b=0):
        x = abs(x)
        if x < 1.0:
            return ((12-9*a-6*b) *x*x*x + (-18+12*a+6*b)*x*x + (6-2*a))/6.0
        elif x < 2.0:
            return ((-a-6*b)*x*x*x + (6*a+30*b)*x*x + (-12*a-48*b)*x + (8*a+24*b))/6.0
        else:
            return 0
    data = np.zeros((size,4), np.float32)
    for i in range(size):
        x = i/float(size-1)
        data[i,0] = MitchellNetravali(x+1)
        data[i,1] = MitchellNetravali(x)
        data[i,2] = MitchellNetravali(1-x)
        data[i,3] = MitchellNetravali(2-x)
    return data

# -----------------------------------------------------------------------------
class FontManagerException(Exception): pass


# -----------------------------------------------------------------------------
class FontManager(object):
    def __init__(self, atlas = None):
        if atlas is None: 
            self.atlas = AtlasBuffer(512, 512, np.float32)
        else:
            self.atlas = atlas
        self.atlas_texture = Texture(self.atlas.data)

        self.filter_kernel = _build_kernel()
        self.filter_texture = Texture(self.filter_kernel,"RGBA","float")
        #self.filter = glagg.spatial_filter.CatRom()
        #self.filter_code = self.filter.get_code()
        #self.filter_texture = Texture(self.filter.LUT,"A","float")
        self.fonts = {}

    def get(self, filename, size=12):
        ''' Get a font described by filename and size'''

        key = '%s-%d' % (os.path.basename(filename), size)
        if key in self.fonts.keys():
            return self.fonts[key]
        font = TextureFont(filename, self.atlas)
        self.fonts[key] = font
        return font
        
