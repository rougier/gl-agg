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
/*
 * Bicubic interpolation fragment shader
 * -------------------------------------
 *
 * From GPU Gems
 * Chapter 24. High-Quality Filtering
 * Kevin Bjorke, NVIDIA
 * http://http.developer.nvidia.com/GPUGems/gpugems_ch24.html
 *
 * Note: This shader require a kernel stored as a 1d texture
 * ----
 *
 * Kernel generation C code:
 * -------------------------
 *
 * // Mitchell Netravali Reconstruction Filter
 * // B = 1,   C = 0   - cubic B-spline
 * // B = 1/3, C = 1/3 - recommended
 * // B = 0,   C = 1/2 - Catmull-Rom spline
 * float MitchellNetravali(float x, float B, float C) {
 *   float ax = fabs(x);
 *   if (ax < 1) {
 *     return ((12 - 9 * B - 6 * C) * ax * ax * ax +
 *             (-18 + 12 * B + 6 * C) * ax * ax + (6 - 2 * B)) / 6;
 *   } else if ((ax >= 1) && (ax < 2)) {
 *     return ((-B - 6 * C) * ax * ax * ax +
 *             (6 * B + 30 * C) * ax * ax + (-12 * B - 48 * C) *
 *             ax + (8 * B + 24 * C)) / 6;
 *   } else {
 *     return 0;
 *   }
 * }
 *
 * // Create a 1D float texture encoding weight for cubic filter
 * GLuint createWeightTexture(int size, float B, float C) {
 *   float *img = new 
 *   float[size * 4];
 *   float *ptr = img;
 *   for(int i = 0; i < size; i++) {
 *     float x = i / (float) (size - 1);
 *     *ptr++ = MitchellNetravali(x + 1, B, C);
 *     *ptr++ = MitchellNetravali(x, B, C);
 *     *ptr++ = MitchellNetravali(1 - x, B, C);
 *     *ptr++ = MitchellNetravali(2 - x, B, C);
 *   }
 *   GLuint texid;
 *   glGenTextures(1, &texid);
 *   GLenum target = GL_TEXTURE_RECTANGLE_NV;
 *   glBindTexture(target, texid);
 *   glTexParameteri(target, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
 *   glTexParameteri(target, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
 *   glTexParameteri(target, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
 *   glTexParameteri(target, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
 *   glPixelStorei(GL_UNPACK_ALIGNMENT, 1);
 *   glTexImage2D(target, 0, GL_FLOAT_RGBA_NV, size, 1, 0,
 *                GL_RGBA, GL_FLOAT, img);
 *   delete [] img;
 *   return texid;
 * }
 */

vec4
cubic_filter(sampler1D kernel, float x, vec4 c0, vec4 c1, vec4 c2, vec4 c3)
{
    vec4 h = texture1D(kernel, x);
    vec4 r = c0 * h.x; // f(x+1)
    r += c1 * h.y;     // f(x)
    r += c2 * h.z;     // f(1-x)
    r += c3 * h.w;     // f(2-x)
    return r;
}

vec4
interpolate (sampler2D texture, sampler1D kernel, vec2 uv, vec2 pixel)
{
    vec2 texel = uv/pixel;
    vec2 f = fract(texel);
    texel = (texel-fract(texel)+vec2(0.001,0.001))*pixel;

    vec4 t0 = cubic_filter(kernel, f.x,
                           texture2D(texture, texel + vec2(-1, -1)*pixel),
                           texture2D(texture, texel + vec2( 0, -1)*pixel),
                           texture2D(texture, texel + vec2( 1, -1)*pixel),
                           texture2D(texture, texel + vec2( 2, -1)*pixel));
    vec4 t1 = cubic_filter(kernel, f.x,
                           texture2D(texture, texel + vec2(-1, 0)*pixel),
                           texture2D(texture, texel + vec2( 0, 0)*pixel),
                           texture2D(texture, texel + vec2( 1, 0)*pixel),
                           texture2D(texture, texel + vec2( 2, 0)*pixel));
    vec4 t2 = cubic_filter(kernel, f.x,
                           texture2D(texture, texel + vec2(-1, 1)*pixel),
                           texture2D(texture, texel + vec2( 0, 1)*pixel),
                           texture2D(texture, texel + vec2( 1, 1)*pixel),
                           texture2D(texture, texel + vec2( 2, 1)*pixel));
    vec4 t3 = cubic_filter(kernel, f.x,
                           texture2D(texture, texel + vec2(-1, 2)*pixel),
                           texture2D(texture, texel + vec2( 0, 2)*pixel),
                           texture2D(texture, texel + vec2( 1, 2)*pixel),
                           texture2D(texture, texel + vec2( 2, 2)*pixel));
    return cubic_filter(kernel, f.y, t0, t1, t2, t3);
}



// Constants
// ------------------------------------
const float glyph_center   = 0.50;
const float outline_center = 0.55;
const float glow_center    = 1.25;

// Uniforms
// ------------------------------------
uniform mat4      u_M, u_V, u_P, u_N;
uniform sampler2D u_font_atlas;
uniform vec2      u_font_atlas_shape;
uniform sampler2D u_uniforms;
uniform vec2      u_uniforms_shape;
uniform sampler1D u_filter_lut;

// Varying
// ------------------------------------
varying vec2  v_texcoord;
varying vec4  v_color;


// Main
// ------------------------------------
void main()
{
    float scale = .2;

    vec2 pixel = 1.0 / u_font_atlas_shape;

    vec4 glyph_color = vec4(0.0,0.0,0.0,1.0);
    vec3 outline_color = vec3(0.0,0.0,0.0);

    // float d = texture2D(u_font_atlas, v_texcoord.xy).a;

    float curr = interpolate(u_font_atlas, u_filter_lut, v_texcoord.xy, pixel).a;
    float prev = interpolate(u_font_atlas, u_filter_lut,
                             v_texcoord.xy - 1.0*pixel, pixel).a;
    float next = interpolate(u_font_atlas, u_filter_lut,
                             v_texcoord.xy + 1.0*pixel, pixel).a; 
    float width = fwidth(curr);
    float alpha = smoothstep(glyph_center-width, glyph_center+width, curr);
/*
    if( (alpha < .5) && (prev < curr) && (curr < next) )
    {
        glyph_color = vec4(0.0,0.0,1.0,1.0);
    }
    else if(  (alpha < .5) && (prev > curr) && (curr > next) ) {
        glyph_color = vec4(1.0,0.0,0.0,1.0);
    }
*/

    // Smooth
    gl_FragColor = vec4(glyph_color.rgb, glyph_color.a*alpha);

    // Outline
    // float mu = smoothstep(outline_center-width, outline_center+width, dist);
    // vec3 rgb = mix(outline_color.rgb, glyph_color.rgb, mu);
    // gl_FragColor = vec4(rgb, max(alpha,mu));
}
