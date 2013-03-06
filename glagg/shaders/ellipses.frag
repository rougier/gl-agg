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

// Varying
// ------------------------------------
varying vec4  v_color;
varying vec2  v_position;
varying vec2  v_texcoord;
varying vec2  v_radius;
varying float v_linewidth;
varying float v_antialias;
void main()
{
    // If color is fully transparent we just discard the fragment
    if( v_color.a < 0.0 )
    {
        discard;
    }

    float t = v_linewidth/2.0-v_antialias;
    vec2 uv = v_position;
    float x2 = uv.x * uv.x;
    float y2 = uv.y * uv.y;

    float a2 = v_radius.x+v_linewidth/2.;
    a2 *= a2;
    float b2 = v_radius.y+v_linewidth/2.;
    b2 *= b2;

    float d1 = sqrt(x2/a2 + y2/b2);
    float width1 = fwidth(d1)*v_antialias/1.25;
    float alpha1  = smoothstep(1.0 - width1, 1.0 + width1, d1);

    a2 = v_radius.x - v_linewidth/2.;
    a2 *= a2;
    b2 = v_radius.y - v_linewidth/2.;
    b2 *= b2;
    float d2 = sqrt(x2/a2 + y2/b2);
    float width2 = fwidth(d2)*v_antialias/1.25;
    float alpha2  = smoothstep(1.0 + width2, 1.0 - width2, d2);

    float alpha = (1.0-max(alpha1,alpha2));
    gl_FragColor = vec4(v_color.rgb, alpha*v_color.a);

}
