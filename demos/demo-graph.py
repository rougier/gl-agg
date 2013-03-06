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
from scipy.spatial import cKDTree
from scipy.spatial.distance import cdist


def graph(links = [(0,1), (1,2), (2,3), (3,0), (0,2), (1,3),
                   (3,4), (4,5), (5,6), (6,7),
                   (7,8), (8,9), (9,10), (10,7), (8,10), (7,9) ]):

    ntype = np.dtype( [('position', 'f4', 2),
                       ('previous', 'f4', 2),
                       ('weight',   'f4', 1),
                       ('charge',   'f4', 1),
                       ('fixed',    'b',  1)] )
    ltype = np.dtype( [('source',   'i4', 1),
                       ('target',   'i4', 1),
                       ('strength', 'f4', 1),
                       ('distance', 'f4', 1)] )

    L = np.array(links).reshape(len(links),2)
    L -= L.min()

    n = L.max()+1
    nodes = np.zeros(n, ntype)
    nodes['position'] = np.random.uniform(256-32, 256+32, (n,2))
    nodes['previous'] = nodes['position']
    nodes['fixed'] = False
    nodes['weight'] = 1
    nodes['charge'] = 1

    l = len(L)
    links = np.zeros( n+l, ltype)
    links[:n]['source'] = np.arange(0,n)
    links[:n]['target'] = np.arange(0,n)
    links[n:]['source'] = L[:,0]
    links[n:]['target'] = L[:,1]
    links['distance'] = 25
    links['strength'] = 5

    I = np.argwhere(links['source']==links['target'])
    links['distance'][I] = links['strength'][I] = 0

    return nodes,links
    

# -----------------------------------------------------------------------------
def relaxation(nodes, links):
    """ Gauss-Seidel relaxation for links """

    sources_idx = links['source']
    targets_idx = links['target']
    sources   = nodes[sources_idx]
    targets   = nodes[targets_idx]
    distances = links['distance']
    strengths = links['strength']

    D = (targets['position'] - sources['position'])
    L = np.sqrt((D*D).sum(axis=1))

    # This avoid to test L != 0 (I = np.where(L>0))
    L = np.where(L,L,np.NaN)
    L = strengths * (L-distances) /L

    # Replace nan by 0, i.e. where L was 0
    L = np.nan_to_num(L)

    D *= L.reshape(len(L),1)
    K = sources['weight'] / (sources['weight'] + targets['weight'])
    K = K.reshape(len(K),1)

    # Note that a direct  nodes['position'][links['source']] += K*D*(1-F)
    # would't work as expected because of repeated indices
    F = nodes['fixed'][sources_idx].reshape(len(links),1)
    W = K*D*(1-F) * 0.1
    nodes['position'][:,0] += np.bincount(sources_idx, W[:,0], minlength=len(nodes))
    nodes['position'][:,1] += np.bincount(sources_idx, W[:,1], minlength=len(nodes))

    F = nodes['fixed'][targets_idx].reshape(len(links),1)
    W = (1-K)*D*(1-F) * 0.1
    nodes['position'][:,0] -= np.bincount(targets_idx, W[:,0], minlength=len(nodes))
    nodes['position'][:,1] -= np.bincount(targets_idx, W[:,1], minlength=len(nodes))

# -----------------------------------------------------------------------------
def repulsion(nodes, links):
    P = nodes['position']
    n = len(P)
    X,Y = P[:,0],P[:,1]
    dX,dY = np.subtract.outer(X,X), np.subtract.outer(Y,Y)
    dist = cdist(P,P)
    dist = np.where(dist, dist, 1)
    D = np.empty((n,n,2))
    D[...,0] = dX/dist
    D[...,1] = dY/dist
    D = np.nan_to_num(D)
    R = D.sum(axis=1)
    L = np.sqrt(((R*R).sum(axis=0)))
    R /= L
    F = nodes['fixed'].reshape(len(nodes),1)
    P += 5*R*(1-F)

# -----------------------------------------------------------------------------
def attraction(nodes, links):
    P = nodes['position']
    F = nodes['fixed'].reshape(len(nodes),1)
    P += 0.01*((256,256) - P) * (1-F)

# -----------------------------------------------------------------------------
def integration(nodes, links):
    P = nodes['position'].copy()
    F = nodes['fixed'].reshape(len(nodes),1)
    nodes['position'] -= ((nodes['previous']-P)*.9) * (1-F)
    nodes['previous'] = P


# -------------------------------------
def on_display():
    gl.glClearColor(1,1,1,1);
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    lines.draw()
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
    nodes['fixed'] = False
    nodes['weight'] = 1
    if state == 0:
        _,_,w,h = gl.glGetIntegerv( gl.GL_VIEWPORT )
        P = nodes['position'] -  (x,h-y)
        D = np.sqrt((P**2).sum(axis=1))
        index = np.argmin(D)
        if D[index] < 10:
            nodes['fixed'][index] = True
            nodes['weight'][index] = 0.01
            drag = True


# -------------------------------------
def on_motion(x, y):
    global drag, mouse, index
    if drag:
        _,_,w,h = gl.glGetIntegerv( gl.GL_VIEWPORT )
        nodes['position'][index] = x,h-y

        P = nodes['position']
        circles.vertices.data['a_center'] = np.repeat(P,4,axis=0)
        circles._vbuffer._dirty = True
        src = nodes[links['source']]['position']
        tgt = nodes[links['target']]['position']
        src = np.repeat(src,4,axis=0)
        lines.vertices.data['a_p0'] = src
        tgt = np.repeat(tgt,4,axis=0)
        lines.vertices.data['a_p1'] = tgt
        lines._vbuffer._dirty = True

    glut.glutPostRedisplay()


# -------------------------------------
def on_timer(fps):

    relaxation(nodes,links)
    repulsion(nodes,links)
    attraction(nodes,links)
    integration(nodes,links)

    # Update collection
    P = nodes['position']
    circles.vertices.data['a_center'] = np.repeat(P,4,axis=0)
    circles._vbuffer._dirty = True
    src = nodes[links['source']]['position']
    tgt = nodes[links['target']]['position']
    src = np.repeat(src,4,axis=0)
    lines.vertices.data['a_p0'] = src
    tgt = np.repeat(tgt,4,axis=0)
    lines.vertices.data['a_p1'] = tgt
    lines._vbuffer._dirty = True

    glut.glutTimerFunc(1000/fps, on_timer, fps)
    glut.glutPostRedisplay()



# -----------------------------------------------------------------------------
if __name__ == '__main__':
    from glagg import LineCollection, CircleCollection

    glut.glutInit(sys.argv)
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGB | glut.GLUT_DEPTH)
    glut.glutCreateWindow("Dynamic graph")
    glut.glutReshapeWindow(512,512)
    glut.glutDisplayFunc(on_display)
    glut.glutReshapeFunc(on_reshape)
    glut.glutKeyboardFunc(on_keyboard)
    glut.glutMouseFunc(on_mouse)
    glut.glutMotionFunc(on_motion)


    nodes,links = graph( )

    circles = CircleCollection()
    lines = LineCollection()
    for node in nodes:
        position = node['position']
        circles.append(center = position, radius=5, linewidth=2,
                       fg_color=(1,1,1,1), bg_color=(1,.5,.5,1))

    src = nodes[links['source']]['position']
    tgt = nodes[links['target']]['position']
    V = np.array(zip(src,tgt)).reshape(2*len(src),2)
    lines.append(V, linewidth=1.5, color=(0.75,0.75,0.75,1.00))
    
    drag,index = False, -1

    fps = 60
    glut.glutTimerFunc(1000/fps, on_timer, fps)
    glut.glutMainLoop()


