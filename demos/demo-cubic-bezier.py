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
    paths.clear()
    circles.clear()

    points = np.array( [ [ (100.,200.), (100.,300.), (400.,300.), (400.,200.) ],
                         [ (600.,200.), (675.,300.), (975.,300.), (900.,200.) ],
                         [ (100.,500.), ( 25.,600.), (475.,600.), (400.,500.) ],
                         [ (600.,500.), (600.,650.), (900.,350.), (900.,500.) ],
                         [ (100.,800.), (175.,900.), (325.,900.), (400.,800.) ],
                         [ (600.,800.), (625.,900.), (725.,900.), (750.,800.) ],
                         [ (750.,800.), (775.,700.), (875.,700.), (900.,800.) ] ] )
    points /= [1000., 1000.]
    points *= [width, height]
    for (p0,p1,p2,p3) in points:
        add_bezier( p0, p1, p2, p3 )

    gl.glViewport(0, 0, width, height)

# -------------------------------------
def on_keyboard(key, x, y):
    if key == '\033': sys.exit()

# -------------------------------------
def add_bezier(p0,p1,p2,p3):
    vertices = curve4_bezier(p0, p1, p2, p3)
    paths.append(vertices, color=(0.75,0.75,0.75,1.0),
                 linewidth=12.0, linecaps=('<','>'),
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
    glut.glutInitWindowSize(1000, 1000)
    glut.glutCreateWindow("Cubic Bézier curves")
    glut.glutDisplayFunc(on_display)
    glut.glutReshapeFunc(on_reshape)
    glut.glutKeyboardFunc(on_keyboard)

    paths = PathCollection()
    circles = CircleCollection()

    glut.glutMainLoop()
