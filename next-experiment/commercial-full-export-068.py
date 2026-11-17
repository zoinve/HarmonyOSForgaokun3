"""Bound full-frame evidence export; never use the original process memory."""
INNER = r'''
    directory("/data/native-full-068",0700);
    if(chown("/data/native-full-068",3036,3036) || chmod("/data/native-full-068",0700))
        fail("private original composer full-frame evidence directory");
'''
OUTER = r'''
#include "native-full-export-068.h"
static void native_full_export068(pid_t child){
 const int saved068=errno;
 static int attempted068=0;
 if(attempted068 || child<=0 || run<0){errno=saved068;return;}
 char path068[128];snprintf(path068,sizeof(path068),"/proc/%d/root/data/native-full-068",child);
 int source068=open(path068,O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);
 if(source068<0){errno=saved068;return;}
 int ready068=openat(source068,"ready",O_RDONLY|O_NOFOLLOW|O_CLOEXEC);
 if(ready068<0){close(source068);errno=saved068;return;}
 close(ready068);attempted068=1;
 struct full068_export_context context068={source068,run,3036};
 int status068=commercial_bounded010(full068_export_worker,&context068,8000);
 close(source068);
 dprintf(1,"COMMERCIAL068_FULL_EXPORT child=%d status=%d deadline_ms=8000\n",child,status068);
 errno=saved068;
}
'''


def inner(source):
    anchor = '    dprintf(1,"COMMERCIAL016_GRAPHICS original_service_credentials_unchanged=1'
    assert source.count(anchor) == 1
    return source.replace(anchor, INNER + anchor, 1)


def outer(source):
    anchor = 'static void native_original(void)'
    assert source.count(anchor) == 1
    source = source.replace(anchor, OUTER + '\n' + anchor, 1)
    anchor = '                if(elapsed033%15==0 || elapsed033==85 || elapsed033==89)'
    assert source.count(anchor) == 1
    source = source.replace(anchor, '                if(elapsed033%15==0)native_full_export068(child);\n' + anchor, 1)
    anchor = '            hw050_tick(child,1);'
    assert source.count(anchor) == 1
    return source.replace(anchor, '            native_full_export068(child);\n' + anchor, 1)
