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
uniform sampler2D u_dash_atlas;

// Varying
// ------------------------------------
varying vec4  v_fg_color;
varying vec4  v_bg_color;
varying vec2  v_position;
varying vec2  v_texcoord;
varying float v_radius;
varying float v_linewidth;
varying float v_antialias;
varying float v_dash_phase;
varying float v_dash_period;
varying float v_dash_index;
varying vec2  v_dash_caps;
void main()
{
    // If color is fully transparent we just discard the fragment
    if( (v_fg_color.a <= 0.0) && (v_bg_color.a <= 0.0))
    {
        discard;
    }

    float t = v_linewidth/2.0-v_antialias;
    float r = length(v_position);
    float d = abs(r - v_radius) - t;
    if( d < 0.0 )
    {
        gl_FragColor = v_fg_color;
    }
    else
    {
        float alpha = d/v_antialias;
        alpha = exp(-alpha*alpha);
        if (r > v_radius)
        {
            gl_FragColor = vec4(v_fg_color.rgb, alpha*v_fg_color.a);
        }
        else
        {
            gl_FragColor = mix(v_bg_color, v_fg_color, alpha);
        }
    }

//    gl_FragColor = v_bg_color;
/*
    float t = v_linewidth/2.0 - v_antialias;
    float d = abs(length(v_position) - v_radius);

    d = d - t;
    if( d < 0.0 ) {
        gl_FragColor = v_fg_color;
    } else {
        float alpha = d/v_antialias;
        alpha = exp( -alpha*alpha );
        gl_FragColor = vec4( v_fg_color.xyz, alpha*v_fg_color.a );
    }
*/

}
