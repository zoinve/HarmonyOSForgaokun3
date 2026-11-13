/* Bulk accesses to DMA mappings, tiled rotation only in cacheable RAM.
 * Caller retains the original validated dimensions, mutex and DMA syncs. */
#pragma once
#include <cstring>
#include "native-landscape-copy-023.h"
static inline void cached_landscape_copy_024(unsigned char *dst,unsigned pitch,unsigned pw,unsigned ph,
 const unsigned char *src,unsigned stride,unsigned cx,unsigned cy,unsigned cw,unsigned ch,bool rgba,
 std::vector<unsigned char> &input,std::vector<unsigned char> &output)
{
    input.resize(size_t(stride)*(cy+ch));
    output.resize(size_t(pw)*4*ph);
    std::memcpy(input.data(),src,input.size());
    landscape_copy_023(output.data(),pw*4,pw,ph,input.data(),stride,cx,cy,cw,ch,rgba);
    for(unsigned y=0;y<ph;++y)
        std::memcpy(dst+size_t(y)*pitch,output.data()+size_t(y)*pw*4,size_t(pw)*4);
}
