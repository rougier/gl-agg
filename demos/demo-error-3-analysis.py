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
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import numpy as np
import matplotlib
matplotlib.rcParams['toolbar'] = 'None'
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
import matplotlib.patheffects as PathEffects
from path_collection import PathCollection

size = 800,800
dpi = 72.0
figsize= size[0]/float(dpi),size[1]/float(dpi)
fig = plt.figure(figsize=figsize, dpi=dpi, facecolor="white")
axes = fig.add_axes([0.0, 0.0, 1.0, 1.0], frameon=False)
axes.set_xlim(0,size[0])
axes.set_ylim(0,size[1])

def on_key(event):
    if event.key == 'escape': sys.exit()
fig.canvas.mpl_connect('key_press_event', on_key)


lw = 25.0
verts = np.array([[-0.1, -0.5],
                  [ 0.0, +0.5],
                  [+0.1, -0.5]])
verts = verts*200 + (400,400)
codes = [Path.MOVETO, Path.LINETO,Path.LINETO ]
path = Path(verts, codes)
patch = patches.PathPatch(path, facecolor='none', lw=lw, alpha=.25)
patch.set_path_effects([PathEffects.Stroke(capstyle='butt')])
axes.add_patch(patch)


path = PathCollection()
path.append(verts)

w = lw/2.0
P = []
for vertex in path[0].vertices:
    position = vertex['a_position']
    segment  = vertex['a_segment']
    t1  = vertex['a_tangents'][:2]
    t1 /= np.sqrt(((t1*t1)).sum())
    t2  = vertex['a_tangents'][2:]
    t2 /= np.sqrt(((t2*t2)).sum())
    u,v = vertex['a_texcoord']
    angle  = np.arctan2 (t1[0]*t2[1]-t1[1]*t2[0],  t1[0]*t2[0]+t1[1]*t2[1])
    t = t1+t2
    t /= np.sqrt(((t*t)).sum())
    o = np.array([t[1], -t[0]])
    position += v * w * o  / np.cos(angle/2.0);
    P.append(position)


P = np.array(P).reshape(len(P),2)
print P
X,Y = P[:,0],P[:,1]

plt.scatter(X,Y)

dx,dy = P[1]-P[3]
d = np.sqrt(dx*dx+dy*dy)
dx,dy = dx/d,dy/d

X = [X[1]-d*dx,X[1]+lw/2*dx]
Y = [Y[1]-d*dy,Y[1]+lw/2*dy]
plt.plot(X,Y)


"""
position.xy += v * w * o / cos(angle/2.0);
if( angle < 0.0 ) {
    if( u == +1.0 ) {
        u = v_segment.y + v * w * tan(angle/2.0);
    } else {
        u = v_segment.x - v * w * tan(angle/2.0);
    }
} else {
    if( u == +1.0 ) {
        u = v_segment.y + v * w * tan(angle/2.0);
    } else {
        u = v_segment.x - v * w * tan(angle/2.0);
    }
}
"""


plt.xticks([]),plt.yticks([])
plt.show()
