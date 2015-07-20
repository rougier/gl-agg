#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (C) 2013  Nicolas P. Rougier
#
# Distributed under the terms of the BSD License. The full license is in
# the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------
import os
import numpy
from distutils.core import setup
from distutils.core import setup, Extension
from Cython.Distutils import build_ext

setup( name         = "glagg",
       version      = "1.0",
       packages     = ['glagg',
                       'glagg.sdf'],
       package_data = {'glagg': ['shaders/*.vert',
                                 'shaders/*.frag',
                                 'fonts/Vera.ttf'] },
       cmdclass={'build_ext': build_ext},
       ext_modules=[Extension("glagg.sdf.sdf",
                              sources=["glagg/sdf/_sdf.pyx", "glagg/sdf/sdf.c"],
                              include_dirs=[numpy.get_include()])] )
