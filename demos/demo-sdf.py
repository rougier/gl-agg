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
import sys
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut

# -------------------------------------
def on_display():
    gl.glClearColor(1,1,1,1);
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    collection.draw()
    glut.glutSwapBuffers()

# -------------------------------------
def on_reshape(width, height):
    gl.glViewport(0, 0, width, height)

# -------------------------------------
def on_keyboard(key, x, y):
    if key == '\033': sys.exit()

# -------------------------------------
def on_idle():
    global t, t0, frames
    t = glut.glutGet( glut.GLUT_ELAPSED_TIME )
    frames = frames + 1
    if t-t0 > 2500:
        print "FPS : %.2f (%d frames in %.2f second)" % (
            (frames*1000.0/(t-t0), frames, (t-t0)/1000.0))
        t0, frames = t,0
    glut.glutPostRedisplay()


# -------------------------------------
def on_motion( x, y ):
    global mouse,translate,scale
    _,_,w,h = gl.glGetIntegerv(gl.GL_VIEWPORT)
    y = h-y
    dx,dy = x-mouse[0], y-mouse[1]
    translate = [translate[0]+dx,translate[1]+dy]
    mouse = x,y
    collection.translate = translate
    glut.glutPostRedisplay()

# -------------------------------------
def on_passive_motion( x, y ):
    global mouse
    _,_,w,h = gl.glGetIntegerv(gl.GL_VIEWPORT)
    mouse = x, h-y

# -------------------------------------
def on_scroll(dx, dy):
    global mouse,translate,scale

    x,y = mouse
    s = min(max(0.1,scale+.001*dy*scale), 200)
    translate[0] = x-s*(x-translate[0])/scale
    translate[1] = y-s*(y-translate[1])/scale
    translate = [translate[0], translate[1]]
    scale = s
    collection.scale = s
    collection.translate = translate
    glut.glutPostRedisplay()

# -------------------------------------
def on_wheel(wheel, direction, x, y):
    if wheel == 0:
        on_scroll(0,direction)
    elif wheel == 1:
        on_scroll(direction,0)




# -----------------------------------------------------------------------------
if __name__ == '__main__':
    from glagg.sdf.font_manager import FontManager
    from glagg.sdf.glyph_collection import GlyphCollection

    t0, frames, t = glut.glutGet(glut.GLUT_ELAPSED_TIME), 0, 0
    glut.glutInit(sys.argv)
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGB | glut.GLUT_DEPTH)
    glut.glutInitWindowSize(800, 400)
    glut.glutCreateWindow("Signed Distance Fields [scroll and zoom with mouse]")
    glut.glutDisplayFunc(on_display)
    glut.glutReshapeFunc(on_reshape)
    glut.glutKeyboardFunc(on_keyboard)
    #glut.glutIdleFunc(on_idle)
    glut.glutMotionFunc( on_motion )
    glut.glutPassiveMotionFunc( on_passive_motion )
    # For OSX, see https://github.com/nanoant/osxglut
    # GLUT for Mac OS X fork with Core Profile and scroll wheel support
    try:
        from ctypes import c_float
        from OpenGL.GLUT.special import GLUTCallback
        glutScrollFunc = GLUTCallback(
            'Scroll', (c_float,c_float), ('delta_x','delta_y'),)
        glutScrollFunc(on_scroll)
    except:
        if bool(glut.glutMouseWheelFunc):
            glut.glutMouseWheelFunc(on_wheel)

    mouse = 400,400
    translate = [300,200]
    scale = 1.

    font_manager = FontManager()
    collection = GlyphCollection(font_manager)
    collection.append("Hello World !\nHow are you today ?",
                      rotate=0.0, scale=1, size=48,
                      color=(0,0,0,1),  translate=translate,
                      anchor_x = 'center', anchor_y = 'center')
    glut.glutMainLoop()

