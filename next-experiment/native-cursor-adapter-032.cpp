/* Native scanout cursor bridge for the audited SDK ABI, not an input source.
 * All untouched methods continue to use the original adapter implementation. */
#include "native-cursor-state-032.h"
#include <dlfcn.h>
#include <cstdio>
#include <mutex>
#include <cstring>
namespace {
std::mutex mutex032;
void *original032=nullptr;
void **original_vtable032=nullptr;
void *vtable032[61]{};
CursorWire032 *wire032=nullptr;
CursorSnapshot032 cursor032{0,-1,-1,false};
unsigned reports032=0;
void publish032(void *self)
{
    using Visible=bool(*)(void *);
    cursor032.visible=reinterpret_cast<Visible>(original_vtable032[16])(self);
    if(!wire032)wire032=cursor_map_032(true);
    if(wire032)cursor_publish_032(wire032,cursor032);
    if(reports032++<8)std::fprintf(stderr,"NATIVE_CURSOR032 publish=%d screen=%llu x=%d y=%d visible=%d\n",
        wire032!=nullptr,static_cast<unsigned long long>(cursor032.screen),cursor032.x,cursor032.y,cursor032.visible);
}
void draw032(void *self,uint64_t screen,int32_t x,int32_t y,const void *style,int32_t direction)
{
    using Draw=void(*)(void *,uint64_t,int32_t,int32_t,const void *,int32_t);
    reinterpret_cast<Draw>(original_vtable032[2])(self,screen,x,y,style,direction);
    std::lock_guard<std::mutex> lock(mutex032);
    cursor032.screen=screen;cursor032.x=x;cursor032.y=y;publish032(self);
}
void location032(void *self,int32_t x,int32_t y,uint64_t screen)
{
    using Location=void(*)(void *,int32_t,int32_t,uint64_t);
    reinterpret_cast<Location>(original_vtable032[14])(self,x,y,screen);
    std::lock_guard<std::mutex> lock(mutex032);
    cursor032.screen=screen;cursor032.x=x;cursor032.y=y;publish032(self);
}
void visible032(void *self,bool visible)
{
    std::lock_guard<std::mutex> lock(mutex032);
    reinterpret_cast<void(*)(void *,bool)>(original_vtable032[15])(self,visible);
    publish032(self);
}
}
extern "C" __attribute__((visibility("default"))) void *GetPointerInstance()
{
    std::lock_guard<std::mutex> lock(mutex032);
    if(original032)return original032;
    void *library=dlopen("/system/lib64/libcursor_drawing_adapter032.z.so",RTLD_NOW|RTLD_LOCAL);
    if(!library){std::fprintf(stderr,"NATIVE_CURSOR032 original load failed: %s\n",dlerror());return nullptr;}
    auto factory=reinterpret_cast<void*(*)()>(dlsym(library,"GetPointerInstance"));
    if(!factory)return nullptr;
    void *object=factory();if(!object)return nullptr;
    auto slots=*reinterpret_cast<void***>(object);
    Dl_info info{};
    // Pinned original is hashed at build/boot; refuse to alter a different ABI.
    if(!dladdr(reinterpret_cast<void *>(factory),&info) ||
        uintptr_t(factory)-uintptr_t(info.dli_fbase)!=0xb0f4 ||
        uintptr_t(slots[2])-uintptr_t(info.dli_fbase)!=0xbe84 ||
        slots[14]!=slots[2] || uintptr_t(slots[15])-uintptr_t(info.dli_fbase)!=0xdba0 ||
        uintptr_t(slots[16])-uintptr_t(info.dli_fbase)!=0xdbd4){
        std::fprintf(stderr,"NATIVE_CURSOR032 ABI mismatch: original returned unchanged\n");return object;
    }
    original_vtable032=slots;
    std::memcpy(vtable032,slots-2,sizeof(vtable032));
    vtable032[2+2]=reinterpret_cast<void *>(draw032);
    vtable032[2+14]=reinterpret_cast<void *>(location032);
    vtable032[2+15]=reinterpret_cast<void *>(visible032);
    *reinterpret_cast<void***>(object)=vtable032+2;
    original032=object;
    std::fprintf(stderr,"NATIVE_CURSOR032 original ABI retained; draw/location/visibility bridged\n");
    return object;
}
