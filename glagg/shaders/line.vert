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
// ----------------------------------------------------------------------------
// Rotate v around origin
void rotate( in vec2 v, in float alpha, out vec2 result )
{
    float c = cos(alpha);
    float s = sin(alpha);
    result = vec2( c*v.x - s*v.y,
                   s*v.x + c*v.y );
}


// Uniforms
// ------------------------------------
uniform mat4      u_M, u_V, u_P, u_N;
uniform sampler2D u_uniforms;
uniform vec2      u_uniforms_shape;

// Attributes
// ------------------------------------
attribute vec2 a_p0;
attribute vec2 a_p1;
attribute vec2 a_texcoord;
attribute float a_index;

// Varying
// ------------------------------------
varying vec4  v_color;
varying vec2  v_linecaps;
varying vec2  v_texcoord;
varying float v_length;
varying float v_linewidth;
varying float v_antialias;
varying float v_dash_phase;
varying float v_dash_period;
varying float v_dash_index;
varying vec2  v_dash_caps;
void main()
{
    // Extract uniforms from uniform texture
    float size = u_uniforms_shape.x - 1.0;
    float index = a_index/(u_uniforms_shape.y-1.0);
    int i = 0;
    vec4 _uniform;

    // Get color(4)
    _uniform = texture2D(u_uniforms, vec2(float(i++)/size,index));
    v_color = _uniform;

    // If color is fully transparent we just will discard the fragment later
    if( v_color.a <= 0.0 ) { gl_Position = vec4(0.0,0.0,0.0,1.0);  return; }

    // Get translate(2), scale(1), rotate(1)
    _uniform = texture2D(u_uniforms, vec2(float(i++)/size,index));
    vec2  translate = _uniform.xy;
    float scale     = _uniform.z;
    float theta     = _uniform.w;

    // Get linewidth(1), antialias(1), linecaps(2)
    _uniform = texture2D(u_uniforms, vec2(float(i++)/size,index));
    v_linewidth = _uniform.x;
    v_antialias = _uniform.y;
    v_linecaps  = _uniform.zw;

    // Get dash_phase(1) dash_period(1), dash_index(1), dash_caps(1)
    _uniform = texture2D(u_uniforms, vec2(float(i++)/size,index));
    v_dash_phase  = _uniform.x;
    v_dash_period = _uniform.y;
    v_dash_index  = _uniform.z;
    v_dash_caps.x = _uniform.w;

    // Get dash_caps(1)
    _uniform = texture2D(u_uniforms, vec2(float(i++)/size,index));
    v_dash_caps.y   = _uniform.x;

    // Thickness below 1 pixel are represented using a 1 pixel thickness
    // and a modified alpha
    v_color.a = min(v_linewidth, v_color.a);
    v_linewidth = max(v_linewidth, 1.0);

    // This is the actual half width of the line
    float w = ceil(1.25*v_antialias+v_linewidth)/2.0;

    v_length = length(a_p0-a_p1)*scale;
    float dx = a_texcoord.x;
    float dy = a_texcoord.y;
   
    v_texcoord = vec2(dx*w + (dx+1.0)/2.0*v_length, dy*w);
    vec2 t = normalize(a_p1-a_p0);
    vec2 o = vec2( +t.y, -t.x);
    
    vec2 position = a_p0 + t*(dx*w + (dx+1.0)/2.0*v_length) + o*w*dy;

    // Rotation
    float c = cos(theta);
    float s = sin(theta);
    position.xy = vec2( c*position.x - s*position.y,
                        s*position.x + c*position.y );
    // Translation
    position +=  translate;

    gl_Position = (u_P*(u_V*u_M))*vec4(position,0.0,1.0);
}
