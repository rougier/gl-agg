#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# OpenGL Anti-Grain Geometry (GL-AGG) - Version 0.1
# A high quality OpenGL rendering engine
# Copyright (C) 2012 Nicolas P. Rougier. All rights reserved.
# Contact: Nicolas.Rougier@gmail.com
#          http://code.google.com/p/gl-agg/
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  1. Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#
#  2. Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
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
# ----------------------------------------------------------------------------
import numpy as np
import OpenGL.GL as gl


class DashAtlas(object):
    """  """

    def __init__(self,shape=(64,1024,4)):
        # 512 patterns at max
        self._data      = np.zeros(shape, dtype=np.float32)
        self._texture_id = 0
        self._index      = 0
        self._atlas      = {}

        self['solid']                 = (1e20,0),      (1,1)
        self['densely dotted']        = (0,1),         (1,1)
        self['dotted']                = (0,2),         (1,1)
        self['loosely dotted']        = (0,3),         (1,1)
        self['densely dashed']        = (1,1),         (1,1)
        self['dashed']                = (1,2),         (1,1)
        self['loosely dashed']        = (1,4),         (1,1)
        self['densely dashdotted']    = (1,1,0,1),     (1,1,1,1)
        self['dashdotted']            = (1,2,0,2),     (1,1,1,1)
        self['loosely dashdotted']    = (1,3,0,3),     (1,1,1,1)
        self['densely dashdotdotted'] = (1,1,0,1,0,1), (1,1,1,1)
        self['dashdotdotted']         = (1,2,0,2,0,2), (1,1,1,1,1,1)
        self['loosely dashdotdotted'] = (1,3,0,3,0,3), (1,1,1,1)

        self._dirty = True


    # ---------------------------------
    def __getitem__(self, key):
        return self._atlas[key]


    # ---------------------------------
    def __setitem__(self, key, value):
        data, period = self.make_pattern( value[0], value[1] )
        self._data[self._index] = data
        self._atlas[key] = [self._index/float(self._data.shape[0]), period]
        self._index += 1
        self._dirty = True
        #self.add_pattern(value)


    # ---------------------------------
    def _get_texture_id(self):
        if self._dirty:
            self.upload()
        return self._texture_id
    texture_id = property(_get_texture_id)


    # ---------------------------------
    def make_pattern(self, pattern, caps=[1,1]):
        """ """

        # A pattern is defined as on/off sequence of segments
        # It must be a multiple of 2
        if len(pattern) > 1 and len(pattern) %2:
            pattern = [pattern[0]+pattern[-1]] + pattern[1:-1]
        P = np.array(pattern)

        # Period is the sum of all segment length
        period = np.cumsum(P)[-1]

        # Find all start and end of on-segment only
        C, c = [], 0
        for i in range(0,len(P)+2,2):
            a = max(0.0001,P[i % len(P)])
            b = max(0.0001,P[(i+1) % len(P)])
            C.extend( [c, c + a] )
            c += a+b
        C = np.array(C)

        # Build pattern
        length = self._data.shape[1]
        Z = np.zeros((length,4), dtype=np.float32)
        for i in np.arange(0,len(Z)):
            x = period*(i)/float(len(Z)-1)
            index = np.argmin(abs(C-(x)))
            if index%2 == 0:
                if x <= C[index]: dash_type = +1
                else:             dash_type =  0
                dash_start, dash_end = C[index],C[index+1]
            else:
                if x > C[index]: dash_type = -1
                else:            dash_type =  0
                dash_start, dash_end = C[index-1],C[index]
            Z[i] = C[index], dash_type, dash_start, dash_end
        return Z, period


    # ---------------------------------
    def upload(self):

        gl.glEnable (gl.GL_TEXTURE_2D)
        if not self._texture_id:
            self._texture_id = gl.glGenTextures( 1 )
        gl.glBindTexture( gl.GL_TEXTURE_2D, self._texture_id )
        gl.glPixelStorei( gl.GL_UNPACK_ALIGNMENT, 1 )
        gl.glPixelStorei( gl.GL_PACK_ALIGNMENT, 1 )
        gl.glTexParameterf( gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST )
        gl.glTexParameterf( gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST )
        gl.glTexParameterf( gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT )
        gl.glTexParameterf( gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT )
        gl.glPixelTransferf( gl.GL_ALPHA_SCALE, 1 )
        gl.glPixelTransferf( gl.GL_ALPHA_BIAS, 0 )
        gl.glTexImage2D( gl.GL_TEXTURE_2D, 0, gl.GL_RGBA32F,
                         self._data.shape[1], self._data.shape[0], 0,
                         gl.GL_RGBA, gl.GL_FLOAT, self._data )

        self._dirty = False
