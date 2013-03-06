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
"""
A dynamic buffer is a dynamic 1D numpy array that can be resized when
necessary. Each data that is appended to the buffer is indexed internally such
that it can be later manipulated as a buffer element indexed by a key.

Example:
-------

>>> buffer = DynamicBuffer(int)
>>> buffer.append ( 0 )
>>> buffer.append ( (1,2,3) )
>>> print buffer[0]
[ 0 ]
>>> print buffer[1]
[ 1 2 3 ]
>>> del buffer[0]
>>> print buffer[0]
[ 1 2 3 ]
"""
import numpy as np


# -----------------------------------------------------------------------------
class DynamicBuffer(object):
    """
    A dynamic buffer is a dynamic 1D numpy array that can be resized when
    necessary. Each data that is appended to the buffer is indexed internally
    such that it can be later manipulated as a buffer element indexed by key.
    """

    # ---------------------------------
    def __init__(self, dtype):
        self._data_dtype = dtype
        self._data_size = 0
        self._data_capacity = 64
        self._data = np.zeros(self._data_capacity, dtype)

        self._item_size = 0
        self._item_capacity = 512
        self._item = np.zeros( (self._item_capacity, 2), dtype=int )

        self._dirty = False

        
    # ---------------------------------
    def get_data(self):
        """ Get underlying data array """
        return self._data[:self._data_size]
    data = property(get_data)


    # ---------------------------------
    def get_dtype(self):
        """ Get underlying data type """
        return self._data.dtype
    dtype = property(get_dtype)


    # ---------------------------------
    def get_shape(self):
        """ Get underlying data shape """
        return self._data[:self._data_size].shape
    shape = property(get_shape)


    # ---------------------------------
    def get_capacity(self):
        """ Get current capacity of the undelying array """
        return self._data_capacity
    capacity = property(get_capacity)


    # ---------------------------------
    def clear(self):
        """ Clear buffer """

        self._data_size = 0
        self._item_size = 0
        self._dirty = True


    # ---------------------------------
    def __len__(self):
        """ Get number of items """

        return self._item_size


    # ---------------------------------
    def _get_indices(self, key):
        """ Get actual indices for the given key """

        size = self._item_size
        if type(key) is slice:
            start, stop = key.start, key.stop
            if start is None:
                start = 0
            elif start < 0:
                start = size+start
            if stop is None:
                stop = size
            elif stop < 0:
                stop = size+stop
        else:
            start = key
            if start < 0:
                start = size+start
            stop = start+1
        if start < 0 or start >= size or stop < 0 or stop > size:
            raise IndexError("Index out of range")
        if start == stop:
            return None

        items = self._item[start:stop]
        return start, stop, items[0][0], items[-1][1]


    # ---------------------------------
    def __getitem__(self, key):
        """ x.__getitem__(y) <==> x[y] """
        istart, istop, dstart, dstop = self._get_indices(key)
        return self._data[dstart:dstop]


    # ---------------------------------
    def __setitem__(self, key, data):
        """ x.__setitem__(i, y) <==> x[i]=y """
        istart, istop, dstart, dstop = self._get_indices(key)
        self._data[dstart:dstop] = data
        # Mark buffer as dirty
        self._dirty = True


    # ---------------------------------
    def __delitem__(self, key):
        """ x.__delitem__(y) <==> del x[y] """
        istart, istop, dstart, dstop = self._get_indices(key)

        # Remove data
        size = self._data_size - dstop
        self._data[dstart:dstart+size] = self._data[dstop:dstop+size]
        self._data_size -= dstop-dstart

        # Remove corresponding item and update others
        size = self._item_size - istop
        self._item[istart:istart+size] = self._item[istop:istop+size]
        size = dstop-dstart
        self._item[istart:istop+size] -= size, size
        self._item_size -= istop-istart

        # Mark buffer as dirty
        self._dirty = True


    # ---------------------------------
    def range(self, key):
        """ Get indices range of a key """
        if key >= self._item_size:
            raise IndexError("Index out of range")
        return self._item[key]


    # ---------------------------------
    def append(self, data ):
        """ L.append(object) -- append object to end """

        data = np.array(data).view(self._data_dtype).ravel()
        size = data.size

        # Check if data array is big enough and resize it if necessary
        if self._data_size + size  >= self._data_capacity:
            capacity = int(2**np.ceil(np.log2(self._data_size + size)))
            self._data = np.resize(self._data, capacity)
            self._data_capacity = capacity

        # Store data
        dstart = self._data_size
        dend   = dstart + size
        self._data[dstart:dend] = data
        self._data_size += size

        # Check if item array is big enough and resize it if necessary
        if self._item_size + 1  >= self._item_capacity:
            capacity = int(2**np.ceil(np.log2(self._item_size + 1)))
            self._item = np.resize(self._item, (capacity, 2))
            self._item_capacity = capacity

        # Store data location (= item)
        istart = self._item_size
        iend   = istart + 1
        self._item[istart:iend] = dstart, dend
        self._item_size += 1

        # Mark buffer as dirty
        self._dirty = True

