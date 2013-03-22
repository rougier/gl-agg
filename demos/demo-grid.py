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
import OpenGL.GL as gl

# -------------------------------------
def on_display():
    gl.glClearColor(1,1,1,1);
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    collection.draw()
    glut.glutSwapBuffers()

# -------------------------------------
def on_reshape(width, height):
    gl.glViewport(0, 0, width, height)
    collection[0].size = width, height

# -------------------------------------
def on_keyboard(key, x, y):
    if key == '\033': sys.exit()

# -------------------------------------
def on_motion( x, y ):
    global mouse
    _,_,w,h = gl.glGetIntegerv(gl.GL_VIEWPORT)
    y = h-y
    dx,dy = x-mouse[0], y-mouse[1]
    offset = collection[0].offset
    offset += dx,dy
    mouse = x,y
    collection[0].offset = offset
    collection.update_gbuffer(0)
    glut.glutPostRedisplay()

# -------------------------------------
def on_passive_motion( x, y ):
    global mouse
    _,_,w,h = gl.glGetIntegerv(gl.GL_VIEWPORT)
    mouse = x, h-y

# -------------------------------------
def on_scroll(dx, dy):
    global mouse

    x,y = mouse

    offset = collection._ubuffer[0]['offset'].ravel()
    zoom = collection._ubuffer[0]['zoom']
    z = min(max(0.25,zoom+.001*dy*zoom), 10)
    offset[0] = x-z*(x-offset[0])/zoom
    offset[1] = y-z*(y-offset[1])/zoom
    collection._ubuffer[0]['offset'] = offset[0], offset[1]
    collection._ubuffer[0]['zoom'] = z

    collection.update_gbuffer(0)
    glut.glutPostRedisplay()


# -------------------------------------
def on_wheel(wheel, direction, x, y):
    print "on_wheel", wheel, direction
    if wheel == 0:
        on_scroll(0,direction)
    elif wheel == 1:
        on_scroll(direction,0)

# -------------------------------------
if __name__ == '__main__':
    import sys
    import OpenGL.GLUT as glut
    from glagg import GridCollection

    glut.glutInit(sys.argv)
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGB | glut.GLUT_DEPTH)
    glut.glutInitWindowSize(800, 800)
    glut.glutCreateWindow("Grid everywhere [scroll and zoom with mouse]")
    glut.glutDisplayFunc(on_display)
    glut.glutReshapeFunc(on_reshape)
    glut.glutKeyboardFunc(on_keyboard)
    glut.glutMotionFunc( on_motion )
    glut.glutPassiveMotionFunc( on_passive_motion )

    mouse = 400,400

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

    collection = GridCollection()
    collection.append(size = (800,800))
    glut.glutMainLoop()
