"""Original CLI guide dismissal, a real keyboard event and separate evidence."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
reference = runpy.run_path(str(b / 'commercial-reference-start-036.py'))['REFERENCE']


def instrument(source):
    original = runpy.run_path(str(b / 'commercial-full-frame-068.py'))['HELPER']
    second = original.replace('static void full068_capture(', 'static void full075_capture(').replace(
        'now068<120000000', 'now068<140000000').replace('/data/native-full-068', '/data/native-full-075')
    second = second.replace('#include <sys/stat.h>\n#include "native-full-capture-068.h"\n', '')
    second = second.replace('COMMERCIAL068_FULL_FRAME', 'COMMERCIAL075_FULL_FRAME')
    anchor = 'static void native_capture_012(const Scanout &buffer)'
    assert source.count(anchor) == 1 and 'static void full075_capture(' not in source
    source = source.replace(anchor, second + '\n' + anchor, 1)
    anchor = '    full068_capture(buffer);'
    assert source.count(anchor) == 1
    return source.replace(anchor, anchor + '\n    full075_capture(buffer);', 1)


KEYBOARD = r'''
static void commercial_keyboard075(void)
{
 for(unsigned i075=0;i075<32;++i075){
  char path075[128],name075[256]={0};
  snprintf(path075,sizeof(path075),"/dev/input/event%u",i075);
  int fd075=open(path075,O_RDWR|O_CLOEXEC|O_NOFOLLOW);if(fd075<0)continue;
  if(ioctl(fd075,EVIOCGNAME(sizeof(name075)),name075)<0 ||
     strcmp(name075,"HID 12d1:10b8 Keyboard")){close(fd075);continue;}
  struct input_event event075[2];memset(event075,0,sizeof(event075));
  event075[0].type=EV_KEY;event075[0].code=KEY_LEFTMETA;event075[0].value=1;
  event075[1].type=EV_SYN;event075[1].code=SYN_REPORT;
  ssize_t down075=write(fd075,event075,sizeof(event075));usleep(80000);
  event075[0].value=0;
  ssize_t up075=write(fd075,event075,sizeof(event075));close(fd075);
  dprintf(1,"COMMERCIAL075_KEYBOARD key=LEFTMETA path=%s down_bytes=%zd up_bytes=%zd expected_bytes=%zu response_not_inferred=1\n",
   path075,down075,up075,sizeof(event075));return;
 }
 dprintf(1,"COMMERCIAL075_KEYBOARD keyboard_missing=1 event_not_sent=1\n");
}
'''


def inner(source):
    anchor = 'static void commercial_observer(void)'
    assert source.count(anchor) == 1
    source = source.replace(anchor, KEYBOARD + '\n' + anchor, 1)
    anchor = '    for(unsigned sample=0;sample<48;++sample){'
    assert source.count(anchor) == 1
    # Keyboard timing follows monotonic time, independent of the observer's I/O.
    extra = r'''
    pid_t input075=fork();
    if(input075==0){
        struct timespec now075;
        do {sleep(1);if(clock_gettime(CLOCK_MONOTONIC,&now075))_exit(125);}while(now075.tv_sec<132);
        commercial_keyboard075();_exit(0);
    }
'''
    source = source.replace(anchor, extra + anchor, 1)
    anchor = '    directory("/data/native-full-068",0700);'
    assert source.count(anchor) == 1
    source = source.replace(anchor, '''    directory("/data/native-full-075",0700);
    if(chown("/data/native-full-075",3036,3036) || chmod("/data/native-full-075",0700))
        fail("private original composer second evidence directory");
''' + anchor, 1)
    anchor = '    pid_t observer=fork();if(observer<0)fail("commercial observer");'
    assert source.count(anchor) == 1
    extra = r'''
    pid_t desktop075=fork();if(desktop075<0)fail("reference desktop command launcher");
    if(!desktop075){
        char *const args075[]={"/system/bin/sh","/commercial-direct-desktop-075.sh",NULL};
        char *const env075[]={"PATH=/system/bin/aurora:/system/bin:/vendor/bin","HOME=/",NULL};
        execve(args075[0],args075,env075);_exit(127);
    }
'''
    return source.replace(anchor, extra + anchor, 1)


SNAPSHOT = r'''
struct snapshot075_context { pid_t child; };
static void snapshot075_worker(void *argument)
{
 const struct snapshot075_context *ctx075=argument;
 const char *names075[]={"native-perf-023.trace","native-allocator-073.trace","commercial-direct-desktop075.log"};
 for(unsigned i075=0;i075<3;++i075){
  char path075[256];snprintf(path075,sizeof(path075),"/proc/%d/root/data/%s",ctx075->child,names075[i075]);
  int in075=open(path075,O_RDONLY|O_CLOEXEC|O_NOFOLLOW);
  struct stat before075,after075;
  if(in075<0 || fstat(in075,&before075) || !S_ISREG(before075.st_mode) ||
     before075.st_size<=0 || before075.st_size>16*1024*1024){if(in075>=0)close(in075);continue;}
  char out075[128];snprintf(out075,sizeof(out075),"snapshot075-%s",names075[i075]);
  int fd075=openat(run,out075,O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);
  if(fd075<0){close(in075);_exit(126);}
  unsigned char data075[65536];off_t total075=0;
  while(total075<before075.st_size){
   size_t want075=(size_t)(before075.st_size-total075);if(want075>sizeof(data075))want075=sizeof(data075);
   ssize_t n075=read(in075,data075,want075);
   if(n075<0 && errno==EINTR)continue;
   if(n075<=0 || full068_put(fd075,data075,(size_t)n075))_exit(126);
   total075+=n075;
  }
  if(fstat(in075,&after075) || before075.st_dev!=after075.st_dev || before075.st_ino!=after075.st_ino ||
     after075.st_size<before075.st_size || fsync(fd075) || close(fd075) || close(in075))_exit(126);
  dprintf(1,"COMMERCIAL075_PREFIX_SNAPSHOT name=%s bytes=%lld size_after=%lld append_only_prefix_not_eof=1\n",
   out075,(long long)total075,(long long)after075.st_size);
 }
 if(fsync(run))_exit(126);
}
static void snapshot075(pid_t child)
{
 struct snapshot075_context ctx075={child};
 int result075=commercial_bounded010(snapshot075_worker,&ctx075,8000);
 dprintf(1,"COMMERCIAL075_SNAPSHOT_EXPORT status=%d deadline_ms=8000\n",result075);
}
'''


def outer(source):
    worker = (b / 'native-full-export-068.h').read_text().split('static void full068_export_worker', 1)[1]
    worker = 'static void full075_export_worker' + worker
    for old, new in [('full-source-068.ppm', 'full-source-075.ppm'),
                     ('full-output-068.ppm', 'full-output-075.ppm'), ('full-ready-068', 'full-ready-075')]:
        worker = worker.replace(old, new)
    start = source.index('static void native_full_export068(')
    end = source.index('static void native_original(void)', start)
    helper = source[start:end].replace('native_full_export068', 'native_full_export075').replace(
        '/data/native-full-068', '/data/native-full-075').replace('full068_export_worker', 'full075_export_worker').replace(
        'COMMERCIAL074_FULL_EXPORT', 'COMMERCIAL075_SECOND_FULL_EXPORT')
    anchor = 'static void native_original(void)'
    source = source.replace(anchor, worker + '\n' + helper + '\n' + SNAPSHOT + '\n' + anchor, 1)
    anchor = '            native_full_export068(child);\n            hw050_tick(child,1);'
    assert source.count(anchor) == 1
    source = source.replace(anchor, '            native_full_export068(child);\n            native_full_export075(child);\n            snapshot075(child);\n            hw050_tick(child,1);', 1)
    return source.replace('commercial61-native-074', 'commercial61-native-075').replace('COMMERCIAL074', 'COMMERCIAL075')
