#pragma once
#include "native-cursor-pixels-032.h"
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/mman.h>
#include <unistd.h>
struct alignas(8) CursorWire032 {
    uint32_t sequence,magic;
    uint64_t screen;
    int32_t x,y;
    uint32_t visible;
    unsigned char reserved[36];
};
static_assert(sizeof(CursorWire032)==64,"cursor IPC layout");
static constexpr uint32_t CURSOR_MAGIC032=0x43555232;
static inline void cursor_publish_032(CursorWire032 *w,const CursorSnapshot032 &c)
{
    __atomic_add_fetch(&w->sequence,1,__ATOMIC_ACQ_REL);
    __atomic_store_n(&w->magic,CURSOR_MAGIC032,__ATOMIC_RELAXED);
    __atomic_store_n(&w->screen,c.screen,__ATOMIC_RELAXED);
    __atomic_store_n(&w->x,c.x,__ATOMIC_RELAXED);
    __atomic_store_n(&w->y,c.y,__ATOMIC_RELAXED);
    __atomic_store_n(&w->visible,uint32_t(c.visible),__ATOMIC_RELAXED);
    __atomic_add_fetch(&w->sequence,1,__ATOMIC_RELEASE);
}
static inline bool cursor_read_032(const CursorWire032 *w,CursorSnapshot032 &out)
{
    if(!w)return false;
    uint32_t first=__atomic_load_n(&w->sequence,__ATOMIC_ACQUIRE);
    if(first&1)return false;
    auto magic=__atomic_load_n(&w->magic,__ATOMIC_RELAXED);
    CursorSnapshot032 c{
        __atomic_load_n(&w->screen,__ATOMIC_RELAXED),
        __atomic_load_n(&w->x,__ATOMIC_RELAXED),
        __atomic_load_n(&w->y,__ATOMIC_RELAXED),
        bool(__atomic_load_n(&w->visible,__ATOMIC_RELAXED))};
    __atomic_thread_fence(__ATOMIC_ACQUIRE);
    if(magic!=CURSOR_MAGIC032 || first!=__atomic_load_n(&w->sequence,__ATOMIC_ACQUIRE))return false;
    out=c;return true;
}
static inline CursorWire032 *cursor_map_032(bool writer)
{
    int fd=open("/data/native-cursor032.state",(writer?O_RDWR:O_RDONLY)|O_CLOEXEC|O_NOFOLLOW);
    if(fd<0)return nullptr;
    struct stat s{};
    bool valid=!fstat(fd,&s) && S_ISREG(s.st_mode) && s.st_size==64 &&
        s.st_uid==6696 && s.st_gid==1003 && (s.st_mode&0777)==0640 && s.st_nlink==1;
    void *p=valid?mmap(nullptr,64,writer?(PROT_READ|PROT_WRITE):PROT_READ,MAP_SHARED,fd,0):MAP_FAILED;
    close(fd);return p==MAP_FAILED?nullptr:static_cast<CursorWire032 *>(p);
}
