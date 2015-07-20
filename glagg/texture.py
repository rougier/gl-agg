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
'''
Texture
'''
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLU as glu


# -------------------------------------------------------- TextureException ---
class TextureException(Exception): pass


# ----------------------------------------------------------------- Texture ---
class Texture(object):

    # Types conversion between numpy and OpenGL
    gl_type = { '<i1' : gl.GL_BYTE, 
                '<u1' : gl.GL_UNSIGNED_BYTE,
                '<i2' : gl.GL_SHORT,
                '<u2' : gl.GL_UNSIGNED_SHORT,
                '<i4' : gl.GL_INT, 
                '<u4' : gl.GL_UNSIGNED_INT,
                '<f4' : gl.GL_FLOAT }

    gl_storage =  { 'A'    : {'default' : gl.GL_ALPHA,
                              'ushort'  : gl.GL_ALPHA16 },
                    'LA'   : {'default' : gl.GL_LUMINANCE_ALPHA,
                              'ushort'  : gl.GL_LUMINANCE16_ALPHA16 },
                    'RGB'  : {'default' : gl.GL_RGB,
                              'ushort'  : gl.GL_RGB16 },
                    'RGBA' : {'default' : gl.GL_RGBA,
                              'ushort'  : gl.GL_RGBA16 } }

    def __init__(self, data, format=None, storage='default'):
        '''
        Create a texture from data.

        Parameters
        ----------

        data : numpy array
            data may be an array with following shapes:
                * M
                * MxN
                * MxNx[1,2,3,4]

        format: [None | 'A' | 'LA' | 'RGB' | 'RGBA']
            Specify the texture format to use. Most of times it is possible to
            find it automatically but there are a few cases where it not
            possible to decide. For example an array with shape (M,3) can be
            considered as 2D alpha texture of size (M,3) or a 1D RGB texture of
            size (M,).

        storage : [ 'default' | 'float' ]
            GPU internal storage format.

        '''
        self._id = 0
        self._dirty = True
        self._target = None
        self._data = data
        self._src_type = None
        self._dst_format = None
        self._src_format = None
        self._str_format = format
        self._storage = storage
        self._width = 0
        self._height = 0
        self._parse()


    # ---------------------------------
    def _parse(self):
        """ Parse array shape and type in order to compute texture information. """

        shape = self._data.shape
        dtype = self._data.dtype.str
        if dtype not in self.gl_type.keys():
            raise TextureException(
                """Data type ('%s') in not compatible with gl types""" % dtype)
        self._src_type = self.gl_type[dtype]

        # One dimensional texture
        if len(shape) == 1:
            self._target = gl.GL_TEXTURE_1D
            self._str_format = 'A'
                        
        # One or two dimensional texture
        elif len(shape) == 2:
            self._target = gl.GL_TEXTURE_1D
            if shape[1] == 1 and self._str_format in [None, 'A']:
                self._str_format = 'A'
            elif shape[1] == 2 and self._str_format in [None, 'LA']:
                self._str_format = 'LA'
            elif shape[1] == 3 and self._str_format in [None, 'RGB']:
                self._str_format = 'RGB'
            elif shape[1] == 4 and self._str_format in [None, 'RGBA']:
                self._str_format = 'RGBA'
            else:
                self._target = gl.GL_TEXTURE_2D
                self._str_format = 'A'

        # Two dimensional texture
        elif len(shape) == 3:
            self._target = gl.GL_TEXTURE_2D
            if shape[2] == 1 and self._str_format in [None, 'A']:
                self._str_format = 'A'
            elif shape[2] == 2 and self._str_format in [None, 'LA']:
                self._str_format = 'LA'
            elif shape[2] == 3 and self._str_format in [None, 'RGB']:
                self._str_format = 'RGB'
            elif shape[2] == 4 and self._str_format in [None, 'RGBA']:
                self._str_format = 'RGBA'
            else:
                raise TextureException(
                    """Array shape (%s) not compatible with """
                    """any known texture format.""" % str(shape))
        # Above
        else:
            raise TextureException(
                """Array shape (%s) not compatible with """
                """any known texture format.""" % str(shape))
            
        # Set source and dst format
        self._src_format = self.gl_storage[self._str_format]['default']
        self._dst_format = self.gl_storage[self._str_format][self._storage]

        # Get size
        if self._target == gl.GL_TEXTURE_2D:
            self._width, self._height = shape[1], shape[0]
        else:
            self._width, self._height = shape[0], 0            


    # ---------------------------------
    def get_width(self):
        return self._width
    width = property(get_width)


    # ---------------------------------
    def get_height(self):
        return self._height
    height = property(get_height)


    # ---------------------------------
    def get_format(self):
        return self._str_format
    format = property(get_format)


    # ---------------------------------
    def get_id(self):
        if not self._id or self._dirty:
            self.upload()
        return self._id
    id = property(get_id)


    # ---------------------------------
    def __str__(self):
        if not self._height:
            s = ('1D Texture object: %d (format: %s, storage: %s)\n' %
                 (self.width, self.format, self._storage))
            s += "   " + str(self._src_format) + " -> " + str(self._dst_format)
        else:
            s =  ('2D Texture object: %dx%d (format: %s, storage: %s)\n'
                  % (self.width, self.height, self.format, self._storage))
            s += "   " + str(self._src_format) + " -> " + str(self._dst_format)
        return s


    # ---------------------------------
    def __del__(self):
        if self._id:
            gl.glDeleteTextures([self._id,])


    # ---------------------------------
    def upload(self):
        if not self._dirty:
            return

        if not self._id:
            self._id = gl.glGenTextures(1)
            gl.glBindTexture(self._target, self._id)
            gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
            gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 1)
            gl.glTexParameterf(self._target, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
            gl.glTexParameterf(self._target, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
            gl.glTexParameterf(self._target, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP)
            gl.glTexParameterf(self._target, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP)

        gl.glBindTexture(self._target, self._id)
        if self._target == gl.GL_TEXTURE_1D:
            gl.glTexImage1D (self._target, 0, self._dst_format,
                             self._width, 0,
                             self._src_format, self._src_type, self._data)
        else:
            gl.glTexImage2D (self._target, 0, self._dst_format,
                             self._width, self._height, 0,
                             self._src_format, self._src_type, self._data)
        self._dirty = False



# -----------------------------------------------------------------------------
if __name__ == '__main__':
    print Texture(np.zeros((10),np.float32))
    print
    print Texture(np.zeros((10,4),np.float32), "RGBA")
    print
    print Texture(np.zeros((10,10),np.float32))
    print
    print Texture(np.zeros((10,10,2),np.float32))
    print
    print Texture(np.zeros((10,10,3),np.float32))
    print
    print Texture(np.zeros((10,10,4),np.float32), storage='float')
    print
