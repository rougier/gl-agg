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
import math
import numpy as np
import OpenGL.GL as gl

def on_display():
    gl.glClearColor(1,1,1,1);
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    paths.draw()
    circles.draw()
    glut.glutSwapBuffers()
    
def on_reshape(width, height):
    gl.glViewport(0, 0, width, height)

def on_keyboard(key, x, y):
    if key == '\033': sys.exit()


if __name__ == '__main__':
    import sys
    import OpenGL.GLUT as glut
    from glagg import elliptical_arc, arc
    from glagg import PathCollection, CircleCollection

    glut.glutInit(sys.argv)
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGB | glut.GLUT_DEPTH)
    glut.glutCreateWindow("Elliptical arcs")
    glut.glutReshapeWindow(800,450)
    glut.glutDisplayFunc(on_display)
    glut.glutReshapeFunc(on_reshape)
    glut.glutKeyboardFunc(on_keyboard)

    paths = PathCollection()
    circles = CircleCollection()
    rx,ry = 100, 50
    x1,y1 = 0,ry
    x2,y2 = rx,0
    def add_ellipses(tx,ty, large, sweep):
        vertices = arc(0, 0, rx, ry, 0, 2*math.pi, True)
        paths.append(vertices, translate=(tx,ty),
                     linewidth=.75, dash_pattern='loosely dashed')
        paths.append(vertices, translate=(tx+rx,ty+ry),
                     linewidth=.75, dash_pattern='loosely dashed')

        circles.append((0,0), 3.5, translate=(tx+x1,ty+y1))
        circles.append((0,0), 3.5, translate=(tx+x2,ty+y2))
        vertices = elliptical_arc(x1,y1, rx, ry, 0, large, sweep, x2,y2)
        paths.append(vertices, translate=(tx,ty), linewidth=2, color=(1,0,0,1))

    add_ellipses(150,100,True,False)
    add_ellipses(525,100,True,True)
    add_ellipses(150,300,False,False)
    add_ellipses(525,300,False,True)

    glut.glutMainLoop()
