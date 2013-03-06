#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (C) 2009,2010,2011  Nicolas P. Rougier
#
# Distributed under the terms of the BSD License. The full license is in
# the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------
import os
from distutils.core import setup

setup( name         = "glagg",
       version      = "1.0",
       packages     = ['glagg'],
       package_data = {'glagg': ['shaders/*.vert',
                                 'shaders/*.frag'] } )
