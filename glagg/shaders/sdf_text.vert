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
uniform sampler2D u_font_atlas;
uniform vec2      u_font_atlas_shape;
uniform sampler2D u_uniforms;
uniform vec2      u_uniforms_shape;
uniform sampler1D u_kernel;

// Attributes
// ------------------------------------
attribute vec2  a_position;
attribute vec2  a_texcoord;
attribute vec4  a_glyphtex;
attribute float a_index;

// Varying
// ------------------------------------
varying vec2  v_texcoord;
varying vec4  v_color;
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

    // Scaling
    vec2 position = a_position*scale;


    // Rotation
    float c = cos(theta);
    float s = sin(theta);
    position.xy = vec2( c*position.x - s*position.y,
                        s*position.x + c*position.y );

    // Translation
    position +=  translate;

    // 
    v_texcoord = a_texcoord;
    /*
    vec2 pixel = 1.0/u_font_atlas_shape;
    if( a_texcoord.x == a_glyphtex.x)
    {
        float dx = position.x - floor(position.x);
        position.x = floor(position.x);
        v_texcoord.x -= dx * pixel.x/scale;
    }
    else
    {
        float dx = ceil(position.x) - position.x;
        position.x = ceil(position.x);
        v_texcoord.x += dx * pixel.x/scale;
    }
    */

    gl_Position = (u_P*(u_V*u_M))*vec4(position,0.0,1.0);
}
