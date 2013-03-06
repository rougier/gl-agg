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

float
compute_alpha(float d, float width, float antialias)
{
    d -= width/2.0 - antialias;
    if( d < 0.0 )
    {
        return 1.0;
    }
    else
    {
        float alpha = d/antialias;
        return exp(-alpha*alpha);
    }
}


// Uniforms
// ------------------------------------
uniform mat4      u_M, u_V, u_P, u_N;
uniform sampler2D u_dash_atlas;
uniform sampler2D u_gbuffer;
uniform vec2      u_gbuffer_shape;

// Varying
// ------------------------------------
varying float v_gindex;
varying vec2  v_size;
varying float v_antialias;
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
void main()
{
    float x = v_position.x;
    float y = v_position.y;

    float Mx = abs(x - texture2D(u_gbuffer, vec2(v_texcoord.x, v_gindex )).x - 0.315);
    float My = abs(y - texture2D(u_gbuffer, vec2(v_texcoord.y, v_gindex )).y - 0.315);
    float mx = abs(x - texture2D(u_gbuffer, vec2(v_texcoord.x, v_gindex )).z - 0.315);
    float my = abs(y - texture2D(u_gbuffer, vec2(v_texcoord.y, v_gindex )).w - 0.315);


    // Major grid
    float M = min(Mx,My);
    // Minor grid
    float m = min(mx,my);

    /*
    vec4 dash_color;
    vec2 dash, dash_caps;
    float dash_period, dash_phase, dash_width, dash_index;
    if( M < m ) {
        dash_color = v_major_grid_color;
        dash_caps  = v_major_dash_caps;
        dash_phase = v_major_dash_phase;
        dash_width = v_major_grid_width * 2.0;
        dash_period= v_major_dash_period;
        dash_index = v_major_dash_index;
        if ( Mx < My ) {
            dash.x = y;
            dash.y = abs(Mx);
        } else {
            dash.x = x;
            dash.y = abs(My);
        }
    } else {
        dash_color = v_minor_grid_color;
        dash_caps  = v_minor_dash_caps;
        dash_phase = v_minor_dash_phase;
        dash_width = v_minor_grid_width * 5.0;
        dash_period= v_minor_dash_period;
        dash_index = v_minor_dash_index;
        if ( mx < my ) {
            dash.x = y;
            dash.y = abs(mx);
        } else {
            dash.x = x;
            dash.y = abs(my);
        }
    }

    float freq = dash_period * dash_width;
    float u = mod( dash.x + dash_phase*dash_width, freq );
    vec4 v = texture2D(u_dash_atlas, vec2(u/freq, dash_index));
    float dash_center= v.x * dash_width;
    float dash_type  = v.y;
    float _start = v.z * dash_width;
    float _stop  = v.w * dash_width;
    float dash_start = dash.x - u + _start;
    float dash_stop  = dash.x - u + _stop;

    float d ;
    float t = dash_width/2.0 - v_antialias;

    // Dash cap left
    if( dash_type < 0.0 )
    {
        float u = max( u-dash_center , 0.0 );
        d = cap( int(dash_caps.x), abs(u), dash.y, t);
    }
    // Dash body (plain)
    else if( dash_type == 0.0 )
    {
        d = abs(dash.y);
    }
    // Dash cap right
    else if( dash_type > 0.0 )
    {
        float u = max( dash_center-u, 0.0 );
        d = cap( int(dash_caps.x), abs(u), dash.y, t);
    }
    d = d - t;
    if( d < 0.0 )
    {
        gl_FragColor = dash_color;
    }
    else
    {
        d /= v_antialias;
        gl_FragColor = vec4(dash_color.xyz, exp(-d*d)*dash_color.a);
    }
    */




    vec4 color = v_major_grid_color;
    float alpha1 = compute_alpha( M, v_major_grid_width, v_antialias);
    float alpha2 = compute_alpha( m, v_minor_grid_width, v_antialias);
    float alpha  = alpha1;
    if( alpha2 > alpha1*1.5 )
    {
        alpha = alpha2;
        color = v_minor_grid_color;
    }

    // Top major ticks
    if( y > (v_size.y-v_major_tick_size.y) )
    {
        float a = compute_alpha(Mx, v_major_tick_width, v_antialias);
        if (a > alpha)
        {
            alpha = a;
            color = v_major_tick_color;
        }
    }

    // Bottom major ticks
    else if( y < v_major_tick_size.y )
    {
        float a = compute_alpha(Mx, v_major_tick_width, v_antialias);
        if (a > alpha)
        {
            alpha = a;
            color = v_major_tick_color;
        }
    }

    // Left major ticks
    if( x < v_major_tick_size.x )
    {
        float a = compute_alpha(My, v_major_tick_width, v_antialias);
        if (a > alpha )
        {
            alpha = a;
            color = v_major_tick_color;
        }
    }

    // Right major ticks
    else if( x > (v_size.x-v_major_tick_size.x) )
    {
        float a = compute_alpha(My, v_major_tick_width, v_antialias);
        if (a > alpha )
        {
            alpha = a;
            color = v_major_tick_color;
        }
    }

    // Top minor ticks
    if( y > (v_size.y-v_minor_tick_size.y) )
    {
        float a = compute_alpha(mx, v_minor_tick_width, v_antialias);
        if (a > alpha)
        {
            alpha = a;
            color = v_minor_tick_color;
        }
    }

    // Bottom minor ticks
    else if( y < v_minor_tick_size.y )
    {
        float a = compute_alpha(mx, v_minor_tick_width, v_antialias);
        if (a > alpha)
        {
            alpha = a;
            color = v_minor_tick_color;
        }
    }

    // Left minor ticks
    if( x < v_minor_tick_size.x )
    {
        float a = compute_alpha(my, v_minor_tick_width, v_antialias);
        if (a > alpha )
        {
            alpha = a;
            color = v_minor_tick_color;
        }
    }

    // Right minor ticks
    else if( x > (v_size.x-v_minor_tick_size.x) )
    {
        float a = compute_alpha(my, v_minor_tick_width, v_antialias);
        if (a > alpha )
        {
            alpha = a;
            color = v_minor_tick_color;
        }
    }

    gl_FragColor = vec4(color.xyz, alpha*color.a);
}
