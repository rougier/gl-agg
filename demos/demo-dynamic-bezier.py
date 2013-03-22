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
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    paths.draw()
    circles.draw()
    glut.glutSwapBuffers()

# -------------------------------------
def on_reshape(width, height):
    gl.glViewport(0, 0, width, height)

# -------------------------------------
def on_keyboard(key, x, y):
    if key == '\033': sys.exit()

# -------------------------------------
def on_mouse(button, state, x, y):
    global drag, index
    drag = False

    if state == 0:
        _,_,w,h = gl.glGetIntegerv( gl.GL_VIEWPORT )
        P = points.reshape(4,2) - (x,h-y)
        D = np.sqrt((P**2).sum(axis=1))
        index = np.argmin(D)
        circles.radius = 4
        if D[index] < 8:
            circles[index].radius = 7
            drag = True

# -------------------------------------
def on_motion(x, y):
    global drag, mouse, index
    if drag:
        _,_,w,h = gl.glGetIntegerv( gl.GL_VIEWPORT )
        points[index] = x,h-y
        paths.clear()
        circles.clear()
        add_bezier( *points )
        circles[index].radius = 7
    glut.glutPostRedisplay()

# -------------------------------------
def on_passive_motion(x, y):
    _,_,_,h = gl.glGetIntegerv( gl.GL_VIEWPORT )
    P  = points - (x,h-y)
    D = np.sqrt((P**2).sum(axis=1))
    index = np.argmin(D)
    circles.radius = 4
    if D[index] < 8:
        circles[index].radius = 8
    glut.glutPostRedisplay()

# -------------------------------------
def add_bezier(p0,p1,p2,p3):
    vertices = curve4_bezier(p0, p1, p2, p3)
    paths.append(vertices, color=(0.75,0.75,0.75,1.0),
                 linewidth=24.0, linecaps=('<','>'),
                 dash_pattern = 'densely dashed', dash_caps=('<','>') )

    paths.append((p0,p1), color=(0.0,0.0,1.0,1.0), dash_pattern='solid')
    paths.append((p2,p3), color=(0.0,0.0,1.0,1.0), dash_pattern='solid')
    circles.append( center = p0, radius = 4, fg_color=(0.0,0.0,1.0,1.0) )
    circles.append( center = p1, radius = 4, fg_color=(0.0,0.0,1.0,1.0) )
    circles.append( center = p2, radius = 4, fg_color=(0.0,0.0,1.0,1.0) )
    circles.append( center = p3, radius = 4, fg_color=(0.0,0.0,1.0,1.0) )


# -----------------------------------------------------------------------------
if __name__ == '__main__':
    import sys
    import OpenGL.GLUT as glut

    from glagg import curve3_bezier, curve4_bezier
    from glagg import PathCollection, CircleCollection

    glut.glutInit(sys.argv)
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGB | glut.GLUT_DEPTH)
    glut.glutInitWindowSize(800, 800)
    glut.glutCreateWindow("Dynamic cubic Bézier curve [drag handles with mouse]")
    glut.glutDisplayFunc(on_display)
    glut.glutReshapeFunc(on_reshape)
    glut.glutKeyboardFunc(on_keyboard)
    glut.glutMouseFunc(on_mouse)
    glut.glutMotionFunc(on_motion)
    glut.glutPassiveMotionFunc(on_passive_motion)

    paths = PathCollection()
    circles = CircleCollection()
    drag,index = False, -1
    points = np.array( [ (100.,400.), (400.,700.),
                         (500.,100.), (700.,400.) ] )
    add_bezier(*points)

    glut.glutMainLoop()
