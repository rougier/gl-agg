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
from agg_setup import *

radius = 255.0
theta, dtheta = 0, 5.5/180.0*np.pi
for i in range(500):
    xc, yc = 256, 256+32
    r = 10.1-i*0.02

    x0 = xc + np.cos(theta)*radius*.925
    y0 = yc + np.sin(theta)*radius*.925
    x1 = xc + np.cos(theta)*radius*1.00
    y1 = yc + np.sin(theta)*radius*1.00
    verts = np.array( [(x0, y0), (x1, y1)] )
    codes = [Path.MOVETO, Path.LINETO ]
    path = Path(verts, codes)
    patch = patches.PathPatch(path, facecolor='none', lw=1.0)
    patch.set_path_effects([PathEffects.Stroke(capstyle='round')])
    axes.add_patch(patch)

    radius -= 0.45
    theta += dtheta

for i in range(0,49):
    thickness = (i+1)/10.0
    x0 = 20+i*10
    y0 = 10
    x1 = x0
    y1 = y0+12

    verts = np.array( [(x0, y0), (x1, y1)] )
    codes = [Path.MOVETO, Path.LINETO ]
    path = Path(verts, codes)
    patch = patches.PathPatch(path, facecolor='none', lw=thickness)
    patch.set_path_effects([PathEffects.Stroke(capstyle='round')])
    axes.add_patch(patch)

fig.savefig('agg-lines.png')
plt.show()
