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
uniform vec3      u_font_atlas_shape;
uniform sampler2D u_uniforms;
uniform vec2      u_uniforms_shape;


// Varying
// ------------------------------------
varying vec2  v_texcoord;
varying vec4  v_color;
varying float v_shift;
varying float v_gamma;
void main()
{
    vec3 shape = u_font_atlas_shape;
    vec4 color = v_color;
    vec2 uv = v_texcoord.xy;

    // LCD Off
    if( shape.z == 1.0 )
    {
        float a = texture2D(u_font_atlas, uv).a;
        gl_FragColor = gl_Color * pow( a, 1.0/v_gamma );
        return;
    }

    // LCD On
    vec4 current = texture2D(u_font_atlas, uv);
    vec4 previous= texture2D(u_font_atlas, uv+vec2(-1.,0.)*(1.0/shape.xy));
    vec4 next    = texture2D(u_font_atlas, uv+vec2(+1.,0.)*(1.0/shape.xy));

    float r = current.r;
    float g = current.g;
    float b = current.b;
    if( v_shift <= 0.333 )
    {
        float z = v_shift/0.333;
        r = mix(current.r, previous.b, z);
        g = mix(current.g, current.r,  z);
        b = mix(current.b, current.g,  z);
    } 
    else if( v_shift <= 0.666 )
    {
        float z = (v_shift-0.33)/0.333;
        r = mix(previous.b, previous.g, z);
        g = mix(current.r,  previous.b, z);
        b = mix(current.g,  current.r,  z);
    }
   else if( v_shift < 1.0 )
    {
        float z = (v_shift-0.66)/0.334;
        r = mix(previous.g, previous.r, z);
        g = mix(previous.b, previous.g, z);
        b = mix(current.r,  previous.b, z);
    }
    
    vec3 rgb = pow(vec3(r,g,b), vec3(1.0/v_gamma));
    gl_FragColor.rgb = rgb * color.rgb;
    gl_FragColor.a = (rgb.r + rgb.g + rgb.b)/3.0 * color.a;
}
