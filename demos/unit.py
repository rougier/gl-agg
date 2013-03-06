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
"""

# -------------------------------------
class UnitException(Exception):
    pass


# -------------------------------------
class Unit(object):
    """ """

    dpi  = 72
    size = [512,512]

    # ---------------------------------
    def __init__(self, value=1.0, scale=1.0, unit='em'):
        self._value = float(value)
        if type(scale) in [int,float]:
            self._scale = float(scale)
        else:
            self._scale = scale
        self._unit = unit

    # ---------------------------------
    def get_scale(self):
        s = self._scale
        if type(s) is float:
            return s
        else:
            return self._scale()
    scale = property(get_scale)

    # ---------------------------------
    def get_unit(self):
        return self._unit
    unit = property(get_unit)

    # ---------------------------------
    def get_value(self):
        return self._value
    value = property(get_value)

    # ------------------------------------------------------------ addition ---
    def __add__(self,other):
        """ x.__add__(y) <==> x+y """

        # Convert to default unit if none given
        if type(other) in [int,float]:
            other = Unit(other, default_unit.scale, default_unit._value)
        v = self._value*self.scale + other._value*other.scale
        return Unit( v/self.scale, self.scale, self._unit)

    def __radd__(self,other):
        """ x.__radd__(y) <==> y+x """

        if type(other) in [int,float]:
            return self._value*self.scale + other

        # All other operations are forbidden
        raise UnitException('Forbidden operation')

    # ---------------------------------------------------------- subtraction ---
    def __sub__(self,other):
        """ x.__sub__(y) <==> x-y """

        # Convert to default unit if none given
        if type(other) in [int,float]:
            other = Unit(other, default_unit.scale, default_unit._value)
        v = self._value*self.scale - other._value*other._scale
        return Unit( v/self.scale, self.scale, self._unit)

    def __rsub__(self,other):
        """ x.__rsub__(y) <==> y-x """

        if type(other) in [int,float]:
            return other - self._value*self.scale

        # All other operations are forbidden
        raise UnitException('Forbidden operation')

    # ------------------------------------------------------ multiplication ---
    def __mul__(self,other):
        """ x.__mul__(y) <==> x*y """

        # Regular multiplication with a scalar
        if type(other) in [int,float]:
            return Unit(self._value*other, self.scale, self._unit)

        # Conversion to another unit
        elif other in units:
            v = self._value*self.scale * other._value
            return Unit(v/other.scale, other.scale, other._unit)

        # All other operations are forbidden
        raise UnitException('Forbidden operation')

    def __rmul__(self,other):
        """ x.__rmul__(y) <==> y*x """

        # Regular multiplication with a scalar
        if type(other) in [int,float]:
            return Unit(self._value*other, self.scale, self._unit)

        # All other operations are forbidden
        raise UnitException('Forbidden operation')

    # ------------------------------------------------------------ division ---
    def __div__(self,other):
        """ x.__div__(y) <==> x/y """

        # Regular division with a scalar
        if type(other) in [int,float]:
            return Unit(self._value/other, self.scale, self._unit)

        # All other operations are forbidden
        raise UnitException('Forbidden operation')

    def __rdiv__(self,other):
        """ x.__rdiv__(y) <==> y/x """

        # All such operations are forbidden
        raise UnitException('Forbidden operation')

    # ---------------------------------
    def __float__(self):
        return float(self._value*self.scale)

    # ---------------------------------
    def __int__(self):
        return int(self._value*self.scale)

    # ---------------------------------
    def __str__(self):
        v = self._value
        if abs(int(v)-v) < 1e-10:
            return "%d %s" % (self._value,self._unit)
        else:
            return "%.3f %s" % (self._value,self._unit)


Unit.dpi   = 72.0
Unit.size = [512,512]
px    = Unit(1,1,'px')
em    = Unit(1, lambda: min(Unit.size[0],Unit.size[1]),'em')
pc    = Unit(1, lambda: min(Unit.size[0],Unit.size[1])/100.0,'%')
inch  = Unit(1, lambda: Unit.dpi/1.000,'in')
cm    = Unit(1, lambda: Unit.dpi/2.540,'cm')
mm    = Unit(1, lambda: Unit.dpi/25.40,'mm')
units = [em, pc, px, cm, mm, inch]
default_unit = px



# -----------------------------------------------------------------------------
if __name__ == '__main__':

    print "Regular conversions"
    print "-------------------"
    print "1 em =", (1*em  )*px
    print "1 pc =", (1*pc  )*px
    print "1 in =", (1*inch)*px
    print "1 cm =", (1*cm  )*px
    print "1 mm =", (1*mm  )*px
    print "1 px =", (1*px  )*px
    print

    print "Operations"
    print "----------"
    print "2*px + 3   =", 2*px+3
    print "3 + 2*px   =", 3+2*px
    print "2*px - 3   =", 2*px-3
    print "3 - 2*px   =", 3-2*px
    print "3 * (2*px) =", 3*(2*px)
    print "(2*px) * 3 =", (2*px)*3
    print "(2*px) / 3 =", (2*px)/3
    print 

    print "Relative units"
    print "--------------"
    print "1 em =", (1*em  )*px
    Unit.size = 200, 200
    print "1 em =", (1*em  )*px

