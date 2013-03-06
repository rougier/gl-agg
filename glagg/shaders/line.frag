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
float
cap( int type, float dx, float dy, float t )
{
    float d = 0.0;
    dx = abs(dx);
    dy = abs(dy);

    // None
    if      (type == 0)  discard;
    // Round
    else if (type == 1)  d = sqrt(dx*dx+dy*dy);
    // Triangle in
    else if (type == 3)  d = (dx+abs(dy));
    // Triangle out
    else if (type == 2)  d = max(abs(dy),(t+dx-abs(dy)));
    // Square
    else if (type == 4)  d = max(dx,dy);
    // Butt
    else if (type == 5)  d = max(dx+t,dy);

    return d;
}


// Uniforms
// ------------------------------------
uniform sampler2D u_dash_atlas;

// Varying
// ------------------------------------
varying vec4  v_color;
varying vec2  v_linecaps;
varying vec2  v_texcoord;
varying float v_length;
varying float v_linejoin;
varying float v_linewidth;
varying float v_antialias;
varying float v_dash_phase;
varying float v_dash_period;
varying float v_dash_index;
varying vec2  v_dash_caps;
void main() 
{
//    gl_FragColor = v_color; return;

    // If color is fully transparent we just discard the fragment
    if( v_color.a <= 0.0 ) { discard; }

    float dx = v_texcoord.x;
    float dy = v_texcoord.y;
    float t = v_linewidth/2.0-v_antialias;
    float width = v_linewidth;

    float line_start = 0.0;
    float line_stop  = v_length;
    float d = 0.0;


    // Solid line
    // ------------------------------------------------------------------------
    if( dx < line_start )
    {
        d = cap( int(v_linecaps.x), abs(dx), abs(dy), t );
    }
    else if( dx > line_stop )
    {
        d = cap( int(v_linecaps.y), abs(dx)-line_stop, abs(dy), t );
    }
    else
    {
        d = abs(dy);
    }

    // Distance to border
    // ------------------------------------------------------------------------
    d = d - t;
    if( d < 0.0 )
    {
        gl_FragColor = v_color;
    }
    else
    {
        d /= v_antialias;
        gl_FragColor = vec4(v_color.xyz, exp(-d*d)*v_color.a);
    }

}
