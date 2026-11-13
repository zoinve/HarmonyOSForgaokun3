// Original SDK is AArch64-only; this ABI-shaped fixture isolates delegation.
#include "native-cursor-adapter-032.cpp"
#include <cassert>
struct Object032 { bool visible=false; unsigned draws=0,locations=0,visibility=0; };
static void original_draw(void *p,uint64_t screen,int32_t x,int32_t y,const void *style,int32_t direction)
{ auto &o=*static_cast<Object032 *>(p);assert(screen==0 && x==400 && y==250 && style==p && direction==0);++o.draws; }
static void original_location(void *p,int32_t x,int32_t y,uint64_t screen)
{ assert(x==501 && y==301 && screen==0);++static_cast<Object032 *>(p)->locations; }
static void original_visible(void *p,bool b)
{ auto &o=*static_cast<Object032 *>(p);o.visible=b;++o.visibility; }
static bool original_get_visible(void *p){return static_cast<Object032 *>(p)->visible;}
int main()
{
    Object032 object;void *slots[59]{};CursorWire032 wire{};CursorSnapshot032 result{};
    slots[2]=reinterpret_cast<void *>(original_draw);slots[14]=reinterpret_cast<void *>(original_location);
    slots[15]=reinterpret_cast<void *>(original_visible);slots[16]=reinterpret_cast<void *>(original_get_visible);
    original_vtable032=slots;wire032=&wire;
    visible032(&object,true);
    draw032(&object,0,400,250,&object,0);
    assert(cursor_read_032(&wire,result) && result.x==400 && result.y==250 && result.visible);
    location032(&object,501,301,0);
    assert(cursor_read_032(&wire,result) && result.x==501 && result.y==301);
    visible032(&object,false);
    assert(cursor_read_032(&wire,result) && !result.visible);
    assert(object.draws==1 && object.locations==1 && object.visibility==2 && !object.visible);
}
