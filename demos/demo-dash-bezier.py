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

def on_display():
    gl.glClearColor(1,1,1,1);
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    collection.draw()
    glut.glutSwapBuffers()

def on_reshape(width, height):
    gl.glViewport(0, 0, width, height)
    collection.scale = min(width, height)

def on_keyboard(key, x, y):
    if key == '\033': sys.exit()

def on_special( key, x, y ):
    if key == glut.GLUT_KEY_LEFT:
        collection.dash_phase -= 0.05
    elif key == glut.GLUT_KEY_RIGHT:
        collection.dash_phase += 0.05
    glut.glutPostRedisplay()


if __name__ == '__main__':
    import sys
    import OpenGL.GLUT as glut

    from glagg import curve3_bezier, curve4_bezier
    from glagg import PathCollection
    from glagg import DashAtlas

    glut.glutInit(sys.argv)
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGB | glut.GLUT_DEPTH)
    glut.glutInitWindowSize(512, 512)
    glut.glutCreateWindow("Dashed & antialiased bezier curve [Arrow keys change offset]")
    glut.glutDisplayFunc(on_display)
    glut.glutReshapeFunc(on_reshape)
    glut.glutKeyboardFunc(on_keyboard)
    glut.glutSpecialFunc(on_special)

    atlas = DashAtlas()
    atlas['custom'] = (.1,.1), (1,1)
    collection = PathCollection( atlas )

    # ---------------------------------
    points = np.array([[.1, .6], [.5, 1.], [.9, .6]])
    vertices = curve3_bezier(*points)
    collection.append(vertices, color=(0.75,0.75,1.00,1.00), linewidth=40,
                      dash_pattern = 'densely dashed')

    # ---------------------------------
    vertices = curve3_bezier(*(points + [0, -0.3]))
    collection.append( vertices, color=(0.75,0.75,1.00,1.0),
                       linewidth=50,  linecaps = ('|','|'),
                       dash_pattern = 'custom', dash_caps=('|','|') )

    glut.glutMainLoop()
