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
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut

def save(display_func, filename="screenshot.png"):
    """  """

    try:
        import OpenGL.GL.EXT.framebuffer_object as fbo
    except ImportError:
        print 'You do not have the framebuffer extension on your video card'
        print 'Cannot save figure'
        return

    x,y,w,h = gl.glGetIntegerv(gl.GL_VIEWPORT)

    # Setup framebuffer
    framebuffer = fbo.glGenFramebuffersEXT(1)
    fbo.glBindFramebufferEXT( fbo.GL_FRAMEBUFFER_EXT, framebuffer)

    # Setup depthbuffer
    depthbuffer = fbo.glGenRenderbuffersEXT( 1 )
    fbo.glBindRenderbufferEXT( fbo.GL_RENDERBUFFER_EXT, depthbuffer )
    fbo.glRenderbufferStorageEXT( fbo.GL_RENDERBUFFER_EXT, gl.GL_DEPTH_COMPONENT, w, h)
    
    # Create texture to render to
    data = np.zeros((w,h,4), dtype=np.ubyte)
    texture = gl.glGenTextures(1)
    gl.glBindTexture( gl.GL_TEXTURE_2D, texture)
    gl.glTexParameteri( gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri( gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexImage2D( gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, w, h, 0,
                     gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, data)
    fbo.glFramebufferTexture2DEXT( gl.GL_FRAMEBUFFER_EXT, gl.GL_COLOR_ATTACHMENT0_EXT,
                                   gl.GL_TEXTURE_2D, texture, 0)
    fbo.glFramebufferRenderbufferEXT( gl.GL_FRAMEBUFFER_EXT, gl.GL_DEPTH_ATTACHMENT_EXT, 
                                      gl.GL_RENDERBUFFER_EXT, depthbuffer)
    status = fbo.glCheckFramebufferStatusEXT( fbo.GL_FRAMEBUFFER_EXT )

    if status != fbo.GL_FRAMEBUFFER_COMPLETE_EXT:
        raise(RuntimeError, 'Error in framebuffer activation')

    display_func()
    glut.glutSwapBuffers()
    data = gl.glReadPixels (x,y,w,h, gl.GL_RGB, gl.GL_UNSIGNED_BYTE)

    from PIL import Image
    #from PIL.ImageCms import profileToProfile
    #ADOBE_RGB_PROFILE = "AdobeRGB1998.icc"
    #SRGB_PROFILE = "./sRGB.icc"
    #RGB_PROFILE = "./RGB.icc"
    image = Image.fromstring('RGB', (w,h), data)
    #profileToProfile(image, RGB_PROFILE, ADOBE_RGB_PROFILE, inPlace=1)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    image.save (filename)


    # Cleanup
    fbo.glBindRenderbufferEXT( fbo.GL_RENDERBUFFER_EXT, 0 )
    fbo.glBindFramebufferEXT( fbo.GL_FRAMEBUFFER_EXT, 0 )
    gl.glDeleteTextures( texture )
    fbo.glDeleteFramebuffersEXT( [framebuffer,] )
