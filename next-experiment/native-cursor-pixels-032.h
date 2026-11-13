#pragma once
#include <cstdint>
#include <cstddef>
#include <cstring>
#include <vector>
struct CursorSnapshot032 { uint64_t screen; int32_t x,y; bool visible; };
static inline bool cursor_point_032(int lw,int lh,int x,int y,int &px,int &py)
{
    if(lw<=0 || lh<=0 || x<0 || y<0 || x>=lw || y>=lh)return false;
    px=lh-1-y;py=x;return true;
}
// The background belongs to the composer, never to a released client buffer.
static inline bool cursor_frame_032(unsigned char *out,size_t size,size_t pitch,
    int pw,int ph,const std::vector<unsigned char> &background,const CursorSnapshot032 &c)
{
    if(!out || pw<=0 || ph<=0 || pw>16384 || ph>16384 || pitch<size_t(pw)*4 ||
        pitch>SIZE_MAX/size_t(ph) || size<pitch*size_t(ph) || background.size()!=pitch*size_t(ph))return false;
    std::memcpy(out,background.data(),background.size());
    if(!c.visible || c.screen!=0 || c.x<0 || c.y<0 || c.x>=ph || c.y>=pw)return true;
    // High-contrast arrow, 24x36 logical pixels; x/y is the actual MMI hotspot.
    for(int y=0;y<36;++y)for(int x=0;x<24;++x){
        bool triangle=y<27 && x<=y*2/3;
        bool stem=y>=18 && y<35 && x>=8+(y-18)/3 && x<=12+(y-18)/3;
        if(!triangle && !stem)continue;
        int px,py;if(!cursor_point_032(ph,pw,c.x+x,c.y+y,px,py))continue;
        bool edge=x==0 || y==0 || (triangle && x>=y*2/3-1) ||
            (stem && (x==8+(y-18)/3 || x==12+(y-18)/3 || y==34));
        auto p=out+size_t(py)*pitch+size_t(px)*4;
        p[0]=p[1]=p[2]=edge?0:255;p[3]=255;
    }
    return true;
}
