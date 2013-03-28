#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# glumpy is an OpenGL framework for the fast visualization of numpy arrays.
# Copyright (C) 2009-2011  Nicolas P. Rougier. All rights reserved.
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
"""
An atlas buffer is a fixed-size 2D numpy array that allows to pack several
smaller 2D arrays. The packing algorithm is based on the article by Jukka
Jylänki : "A Thousand Ways to Pack the Bin - A Practical Approach to
Two-Dimensional Rectangle Bin Packing", February 27, 2010. More precisely, this
is an implementation of the Skyline Bottom-Left algorithm based on C++ sources
provided by Jukka Jylänki at: http://clb.demon.fi/files/RectangleBinPack/

Example
-------

>>> buffer = AtlasBuffer((200,200), np.float)
>>> data = np.ones((10,10), np.float)
>>> x,y,w,h = buffer.add(data)
>>> print x,y
0, 0, 10, 10
"""
import sys
import numpy as np
import OpenGL.GL as gl

# -----------------------------------------------------------------------------
class AtlasBufferException(Exception): pass


# -----------------------------------------------------------------------------
class AtlasBuffer:

    def __init__(self, width=1024, height=1024, dtype=np.float32):
        '''
        Initialize a new atlas of given size.

        Parameters
        ----------

        width : int
            Width of the underlying texture

        height : int
            Height of the underlying texture

        depth : 1 or 3
            Depth of the underlying texture
        '''
        self.width  = width
        self.height = height
        self.nodes  = [ (0,0,self.width), ]
        self.data   = np.zeros((self.height, self.width), dtype)
        self.used   = 0
        self.dirty  = True
        self.texid  = 0

    # ---------------------------------
    def add(self, data, region=None):
        """ Add new data to the atlas.

        Parameters
        ----------
        data: array-like
            Data to be added

        Returns
        -------
            Coordinates of newly allocated area or -1,-1 if no free space found
        """
        if region:
            x,y,w,h = region
        else:
            h,w = data.shape[:2]
            x,y = self.allocate(w,h)
        if x != -1:
            self.data[y:y+h,x:x+w] = data
        return x,y



    # ---------------------------------
    def allocate(self, width, height):
        '''
        Allocate a new area of given size

        Parameters
        ----------
        width : int
            Width of area to allocate

        height : int
            Height of area to allocate

        Returns
        -------
            Coordinates of newly allocated area or -1,-1 if no free space found
        '''

        best_width = sys.maxint
        best_height = sys.maxint
        best_index = -1
        region = 0, 0
        for i in range(len(self.nodes)):
            y = self.rectangle_fits(i, width, height)
            if y >= 0:
                node = self.nodes[i]
                if (y+height < best_height or
                    (y+height == best_height and node[2] < best_width)):
                    best_height = y+height
                    best_index = i
                    best_width = node[2]
                    region = node[0], y


        if best_index == -1:
            return -1,-1

        node = region[0], region[1]+height, width
        self.nodes.insert(best_index, node)
        i = best_index+1
        while i < len(self.nodes):
            node = self.nodes[i]
            prev_node = self.nodes[i-1]
            if node[0] < prev_node[0]+prev_node[2]:
                shrink = prev_node[0]+prev_node[2] - node[0]
                x,y,w = self.nodes[i]
                self.nodes[i] = x+shrink, y, w-shrink
                if self.nodes[i][2] <= 0:
                    del self.nodes[i]
                    i -= 1
                else:
                    break
            else:
                break
            i += 1
        self.merge_skylines()
        self.used += width*height
        return region

    # ---------------------------------
    def rectangle_fits(self, index, width, height):
        """ Check if given rectangle area fits in node """

        node = self.nodes[index]
        x,y = node[0], node[1]
        width_left = width        
        if x+width > self.width:
            return -1
        i = index
        while width_left > 0:
            node = self.nodes[i]
            y = max(y, node[1])
            if y+height > self.height:
                return -1
            width_left -= node[2]
            i += 1
        return y


    # ---------------------------------
    def merge_skylines(self):
        """ Merges all skyline nodes that are at the same level. """

        i = 0
        while i < len(self.nodes)-1:
            node = self.nodes[i]
            next_node = self.nodes[i+1]
            if node[1] == next_node[1]:
                self.nodes[i] = node[0], node[1], node[2]+next_node[2]
                del self.nodes[i+1]
            else:
                i += 1

# -----------------------------------------------------------------------------
if __name__ == '__main__':
    import matplotlib.pyplot as plt

    buffer = AtlasBuffer(200,200, np.float)
    for i in range(100):
        shape = np.random.randint(5,15,2)
        data = np.ones(shape, np.float) * np.random.uniform(0,1) 
        buffer.add(data)
    plt.imshow(buffer.data, interpolation="nearest")
    plt.show()
