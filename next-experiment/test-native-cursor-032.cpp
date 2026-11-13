#include "native-cursor-pixels-032.h"
#include "native-cursor-state-032.h"
#include <cassert>
#include <cstring>
#include <vector>
int main()
{
    CursorWire032 wire{};
    CursorSnapshot032 received{};
    assert(!cursor_read_032(&wire,received));
    CursorSnapshot032 sent{0,201,149,true};
    cursor_publish_032(&wire,sent);
    assert(cursor_read_032(&wire,received));
    assert(received.x==201 && received.y==149 && received.visible && received.screen==0);
    wire.sequence|=1;
    assert(!cursor_read_032(&wire,received)); // Never consume an in-progress update.
    wire.sequence+=1;wire.magic=0;
    assert(!cursor_read_032(&wire,received));
    // Logical 2560x1600 is physically clockwise-rotated, not rescaled.
    int px=-1,py=-1;
    assert(cursor_point_032(2560,1600,0,0,px,py) && px==1599 && py==0);
    assert(cursor_point_032(2560,1600,2559,1599,px,py) && px==0 && py==2559);
    assert(!cursor_point_032(2560,1600,-1,0,px,py));
    assert(!cursor_point_032(2560,1600,2560,0,px,py));
    constexpr int w=64,h=96,pitch=w*4+16;
    std::vector<unsigned char> background(pitch*h,0x67),out(pitch*h,0x99);
    CursorSnapshot032 c{0,4,5,true};
    assert(cursor_frame_032(out.data(),out.size(),pitch,w,h,background,c));
    assert(out!=background);
    for(int y=0;y<h;++y)for(int x=w*4;x<pitch;++x)assert(out[y*pitch+x]==0x67);
    c.visible=false;
    assert(cursor_frame_032(out.data(),out.size(),pitch,w,h,background,c));
    assert(out==background); // Hiding restores the owned background, with no trail.
    c.visible=true;c.screen=1;
    assert(cursor_frame_032(out.data(),out.size(),pitch,w,h,background,c));
    assert(out==background); // This backend only owns screen zero.
    c.screen=0;c.x=h-1;c.y=w-1;
    assert(cursor_frame_032(out.data(),out.size(),pitch,w,h,background,c));
    assert(out!=background); // Edge-clipped arrow still has its hotspot.
    auto before=out;
    assert(!cursor_frame_032(out.data(),out.size()-1,pitch,w,h,background,c));
    assert(out==before); // Reject bad buffers before writing.
    assert(!cursor_frame_032(out.data(),out.size(),w*4-1,w,h,background,c));
}
