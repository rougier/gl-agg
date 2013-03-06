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
import ctypes
import OpenGL.GL as gl

class ShaderException(Exception):
    pass

class Shader:
    def __init__(self, vertex_code = None, fragment_code = None):
        self.uniforms = {}
        self.handle = 0
        self.vertex_code   = vertex_code
        self.fragment_code = fragment_code

    def build(self):
        self.handle = gl.glCreateProgram()
        self.linked = False
        self._build_shader(self.vertex_code, gl.GL_VERTEX_SHADER)
        self._build_shader(self.fragment_code, gl.GL_FRAGMENT_SHADER)
        self._link()

    def _build_shader(self, strings, shader_type):
        count = len(strings)
        if count < 1: 
            return
        shader = gl.glCreateShader(shader_type)
        gl.glShaderSource(shader, strings)
        gl.glCompileShader(shader)
        status = gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS)
        if not status:
            if shader_type == gl.GL_VERTEX_SHADER:
                print gl.glGetShaderInfoLog(shader)
                raise (ShaderException, 'Vertex compilation error')
            elif shader_type == gl.GL_FRAGMENT_SHADER:
                print gl.glGetShaderInfoLog(shader)
                raise (ShaderException, 'Fragment compilation error')
            else:
                print gl.glGetShaderInfoLog(shader)
                raise (ShaderException)
        else:
            gl.glAttachShader(self.handle, shader)

    def _link(self):
        gl.glLinkProgram(self.handle)
        temp = ctypes.c_int(0)
        gl.glGetProgramiv(self.handle, gl.GL_LINK_STATUS, ctypes.byref(temp))
        if not temp:
            gl.glGetProgramiv(self.handle,
                              gl.GL_INFO_LOG_LENGTH, ctypes.byref(temp))
            print gl.glGetProgramInfoLog(self.handle)
            raise(ShaderException, 'Linking error' )
        else:
            self.linked = True

    def bind(self):
        if not self.handle: self.build()
        gl.glUseProgram(self.handle)

    def unbind(self):
        if not self.handle: self.build()
        gl.glUseProgram(0)

    def uniformf(self, name, *vals):
        if not self.handle: self.build()
        loc = self.uniforms.get(name, gl.glGetUniformLocation(self.handle,name))
        self.uniforms[name] = loc
        if len(vals) in range(1, 5):
            { 1 : gl.glUniform1f,
              2 : gl.glUniform2f,
              3 : gl.glUniform3f,
              4 : gl.glUniform4f
            }[len(vals)](loc, *vals)

    def uniformi(self, name, *vals):
        if not self.handle: self.build()
        loc = self.uniforms.get(name, gl.glGetUniformLocation(self.handle,name))
        self.uniforms[name] = loc
        if len(vals) in range(1, 5):
            { 1 : gl.glUniform1i,
              2 : gl.glUniform2i,
              3 : gl.glUniform3i,
              4 : gl.glUniform4i
            }[len(vals)](loc, *vals)

    def uniform_matrixf(self, name, mat):
        if not self.handle: self.build()
        loc = self.uniforms.get(name, gl.glGetUniformLocation(self.handle,name))
        self.uniforms[name] = loc
        gl.glUniformMatrix4fv(loc, 1, False, mat)
