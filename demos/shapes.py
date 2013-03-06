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

def star( r1=0.5, r2=1.0, n=5):
    points = []
    n *= 2
    for i in np.arange(n):
        if i%2: r = r1
        else:   r = r2
        theta = np.pi/12 + 2*np.pi * i/float(n)
        x = r*np.cos(theta)
        y = r*np.sin(theta)
        points.append( [x,y])
    return np.array(points).reshape(n,2)

def asterisk( r1=0.5, r2=1.0, n=6):
    d = np.sin(np.pi/n)*r1
    points = []
    n *= 2
    for i in np.arange(n):
        theta = 2*np.pi *i/float(n)
        if i%2:
            x,y = r1*np.cos(theta), r1*np.sin(theta)
            points.append( [x,y])
        else:
            x,y = r2*np.cos(theta), r2*np.sin(theta)
            o = np.array([x,y])
            o = d*o/np.sqrt((o**2).sum())
            points.append( [x+o[1], y-o[0]] )
            points.append( [x,y])
            points.append( [x-o[1], y+o[0]] )
    return np.array(points).reshape(len(points),2)
