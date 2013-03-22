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

# -------------------------------------
def on_display():
    gl.glClearColor(1,1,1,1);
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT )
    #gl.glPolygonMode( gl.GL_FRONT_AND_BACK, gl.GL_LINE )
    collection.draw()
    glut.glutSwapBuffers()

# -------------------------------------
def on_reshape(width, height):
    gl.glViewport(0, 0, width, height)

# -------------------------------------
def on_keyboard(key, x, y):
    if key == '\033': sys.exit()

# -------------------------------------
def on_special( key, x, y ):
    if key == glut.GLUT_KEY_LEFT:
        collection.dash_phase -= 0.05
    elif key == glut.GLUT_KEY_RIGHT:
        collection.dash_phase += 0.05
    glut.glutPostRedisplay()

# -----------------------------------------------------------------------------
if __name__ == '__main__':
    import sys
    import OpenGL.GLUT as glut
    from shapes import star
    from glagg import PathCollection

    glut.glutInit(sys.argv)
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGB)
    glut.glutInitWindowSize(800, 800)
    glut.glutCreateWindow("Error case 1")
    glut.glutDisplayFunc(on_display)
    glut.glutReshapeFunc(on_reshape)
    glut.glutKeyboardFunc(on_keyboard)
    glut.glutSpecialFunc(on_special)

    collection = PathCollection()
    vertices = []
    for theta in np.linspace(0,2*np.pi,100,endpoint=False):
        x,y = 0.5*np.cos(theta), 0.5*np.sin(theta)
        vertices.append( (x,y) )
    #vertices = star(n=5)
    collection.append( vertices, closed=True, linewidth=25, color = (0,0,0,1),
                       dash_pattern = 'dashed', translate=(400,400), scale=400)

    glut.glutMainLoop()
