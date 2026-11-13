/* Rotate a logical landscape client clockwise into the real portrait panel.
 * Caller validates crop, buffer dimensions/lengths and DMA ownership first. */
#pragma once
#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <vector>
static inline void landscape_copy_023(unsigned char *dst,unsigned pitch,unsigned pw,unsigned ph,
 const unsigned char *src,unsigned stride,unsigned cx,unsigned cy,unsigned cw,unsigned ch,bool rgba)
{
    std::vector<size_t> rows(pw);
    for(unsigned x=0;x<pw;++x)rows[x]=size_t(cy+uint64_t(pw-1-x)*ch/pw)*stride;
    for(unsigned by=0;by<ph;by+=16)for(unsigned bx=0;bx<pw;bx+=16){
        for(unsigned y=by;y<std::min(by+16,ph);++y){
            size_t col=size_t(cx+uint64_t(y)*cw/ph)*4;
            auto out=dst+size_t(y)*pitch;
            for(unsigned x=bx;x<std::min(bx+16,pw);++x){
                auto p=src+rows[x]+col;
                out[x*4]=p[rgba?2:0];out[x*4+1]=p[1];out[x*4+2]=p[rgba?0:2];out[x*4+3]=255;
            }
        }
    }
}
