// -----------------------------------------------------------------------------
// Copyright (c) 2013 Nicolas P. Rougier. All rights reserved.
// 
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are met:
// 
// 1. Redistributions of source code must retain the above copyright notice,
//    this list of conditions and the following disclaimer.
// 
// 2. Redistributions in binary form must reproduce the above copyright
//    notice, this list of conditions and the following disclaimer in the
//    documentation and/or other materials provided with the distribution.
// 
// THIS SOFTWARE IS PROVIDED BY NICOLAS P. ROUGIER ''AS IS'' AND ANY EXPRESS OR
// IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
// MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
// EVENT SHALL NICOLAS P. ROUGIER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
// INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
// (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
// LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
// ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
// (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
// THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
// 
// The views and conclusions contained in the software and documentation are
// those of the authors and should not be interpreted as representing official
// policies, either expressed or implied, of Nicolas P. Rougier.
// -----------------------------------------------------------------------------

// Uniforms
// ------------------------------------
uniform mat4      u_M, u_V, u_P, u_N;
uniform sampler2D u_uniforms;
uniform vec2      u_uniforms_shape;

uniform sampler2D u_gbuffer;
uniform vec2      u_gbuffer_shape;

// Attributes
// ------------------------------------
attribute vec2  a_center;
attribute vec2  a_texcoord;
attribute float a_index;

// Varying
// ------------------------------------
varying float v_gindex;
varying vec2  v_size;
varying vec2  v_position;
varying vec2  v_texcoord;
varying vec2  v_major_grid;
varying vec2  v_minor_grid;
varying vec2  v_major_tick_size;
varying vec2  v_minor_tick_size;
varying vec4  v_major_grid_color;
varying vec4  v_minor_grid_color;
varying vec4  v_major_tick_color;
varying vec4  v_minor_tick_color;
varying float v_major_grid_width;
varying float v_minor_grid_width;
varying float v_major_tick_width;
varying float v_minor_tick_width;
varying float v_major_dash_phase;
varying float v_major_dash_index;
varying float v_major_dash_period;
varying vec2  v_major_dash_caps;
varying float v_minor_dash_phase;
varying float v_minor_dash_index;
varying float v_minor_dash_period;
varying vec2  v_minor_dash_caps;
varying float v_antialias;
void main()
{
    // Extract uniforms from uniform texture
    float size = (u_uniforms_shape.x - 1.0);
    int i = 0;
    float index = a_index/(u_uniforms_shape.y-1.0);

    // gbuffer index is also ubuffer index
    v_gindex = a_index/(u_gbuffer_shape.y-1.0);

    vec4 _uniform;

    // Get translate(2), scale(1), rotate(1)
    _uniform = texture2D(u_uniforms, vec2(float(i++)/size,index));
    vec2  translate = _uniform.xy;
    float scale     = _uniform.z;
    float theta     = _uniform.w;

    // Get major_grid(2), minor_grid(2)
    _uniform = texture2D(u_uniforms, vec2(float(i++)/size,index));
    v_major_grid = _uniform.xy;
    v_minor_grid = _uniform.zw;

    // Get major_tick_size(2), minor_tick_size(2)
    _uniform = texture2D(u_uniforms, vec2(float(i++)/size,index));
    v_major_tick_size = _uniform.xy;
    v_minor_tick_size = _uniform.zw;

    // Get major_grid_color(4)
    v_major_grid_color = texture2D(u_uniforms, vec2(float(i++)/size,index));

    // Get minor_grid_color(4)
    v_minor_grid_color = texture2D(u_uniforms, vec2(float(i++)/size,index));

    // Get major_tick_color(4)
    v_major_tick_color = texture2D(u_uniforms, vec2(float(i++)/size,index));

    // Get minor_tick_color(4)
    v_minor_tick_color = texture2D(u_uniforms, vec2(float(i++)/size,index));

    // Get major_grid_width(1), minor_grid_width(1),
    //     major_tick_width(1), minor_tick_width(1)
    _uniform = texture2D(u_uniforms, vec2(float(i++)/size,index));
    v_major_grid_width = _uniform.x;
    v_minor_grid_width = _uniform.y;
    v_major_tick_width = _uniform.z;
    v_minor_tick_width = _uniform.w;

    // Get size(2), offset(2)
    _uniform = texture2D(u_uniforms, vec2(float(i++)/size,index));
    v_size    = _uniform.xy;
    // v_offset  = _uniform.zw;

    // Get zoom(1), antialias(1), major_dash_phase(1), minoir_dash_phase(1)
    _uniform = texture2D(u_uniforms, vec2(float(i++)/size,index));
    // v_zoom = _uniform.x;
    v_antialias         = _uniform.y;
    v_major_dash_phase  = _uniform.z;
    v_minor_dash_phase  = _uniform.w;

    // Get major_dash_index, major_dash_period(1), major_dash_caps(2)
    _uniform = texture2D(u_uniforms, vec2(float(i++)/size,index));
    v_major_dash_index  = _uniform.x;
    v_major_dash_period = _uniform.y;
    v_major_dash_caps   = _uniform.zw;

    // Get minor_dash_index, minor_dash_period(1), minor_dash_caps(2)
    _uniform = texture2D(u_uniforms, vec2(float(i++)/size,index));
    v_minor_dash_index  = _uniform.x;
    v_minor_dash_period = _uniform.y;
    v_minor_dash_caps   = _uniform.zw;

    // This is the actual half width of the major line width
    float w = ceil(1.25*v_antialias+v_major_grid_width)/2.0;

    // Move vertex position into place
    v_position = a_texcoord*v_size;
    v_texcoord = a_texcoord;
    vec2 position = a_texcoord * v_size;

    // Rotation
    float c = cos(theta);
    float s = sin(theta);
    position = vec2( c*position.x - s*position.y,
                     s*position.x + c*position.y );

    // Translation
    position += translate;

    gl_Position = (u_P*(u_V*u_M))*vec4(position,0.0,1.0);
}
