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
    collection.translate = positions * [width, height]
    gl.glViewport(0, 0, width, height)

def on_key(key, x, y):
    if key == '\033': sys.exit()
    """
    collection.clear()
    p0,p1,p2,p3 = np.random.uniform(200,800,(4,2))
    lw = np.random.uniform(10,20)
    vertices = curve4_bezier(p0,p1,p2,p3)
    #vertices = curve3_bezier(p0,p1,p2)
    collection.append(vertices, linewidth = lw,
                      dash_pattern='densely dotted')
    glut.glutPostRedisplay()
    """

def on_idle():
    collection.rotate += 0.005

    global t, t0, frames
    t = glut.glutGet( glut.GLUT_ELAPSED_TIME )
    frames = frames + 1
    if t-t0 > 2500:
        print "FPS : %.2f (%d frames in %.2f second)" % (frames*1000.0/(t-t0), frames, (t-t0)/1000.0)
        t0, frames = t,0
    glut.glutPostRedisplay()

if __name__ == '__main__':
    import sys
    import OpenGL.GLUT as glut

    from glagg import curve3_bezier, curve4_bezier, PathCollection

    t0, frames, t = 0,0,0
    t0 = glut.glutGet(glut.GLUT_ELAPSED_TIME)
    glut.glutInit(sys.argv)
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGB | glut.GLUT_DEPTH)
    glut.glutInitWindowSize(800, 800)
    glut.glutCreateWindow("Antialiased thick polylines")
    glut.glutDisplayFunc(on_display)
    glut.glutReshapeFunc(on_reshape)
    glut.glutKeyboardFunc(on_key)
    glut.glutIdleFunc(on_idle)

    collection = PathCollection()
    for i in range(2000):
        p0,p1,p2,p3 = np.random.uniform(-1,1,(4,2))
        vertices = curve4_bezier(p0,p1,p2,p3)
        color = np.random.uniform(0,1,4)
        linewidth = np.random.uniform(2,3)
        translate = np.random.uniform(0,1,2)
        scale = np.random.uniform(20,45)
        rotate = np.random.uniform(0,2*np.pi)
        collection.append(
            vertices, color = color, linewidth = linewidth,
            translate = translate, scale=scale, rotate = rotate )
    positions = collection.translate.copy()

    glut.glutMainLoop()
