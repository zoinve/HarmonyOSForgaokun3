"""Persist original-process discovery and pre-control setup boundaries."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-048.py'))
inner = p['inner']
outer = p['outer'].replace('commercial61-native-048', 'commercial61-native-049').replace('COMMERCIAL048', 'COMMERCIAL049').replace('commercial048/', 'commercial049/').replace('events/commercial048', 'events/commercial049')
helper = r'''
static void trace_stage049(const char *stage,long value)
{
    int saved=errno;struct timespec now={0};
    (void)clock_gettime(CLOCK_MONOTONIC,&now);
    dprintf(1,"COMMERCIAL049_TRACE_STAGE stage=%s value=%ld mono=%lld.%09ld\n",stage,value,(long long)now.tv_sec,now.tv_nsec);
    snapshot();errno=saved;
}
'''
anchor = 'static int trace_setup046(pid_t child)'
assert outer.count(anchor) == 1
outer = outer.replace(anchor, helper + anchor, 1)
anchor = '    char path[256],expected[128]={},actual[128]={},text[4096],root[128];'
assert outer.count(anchor) == 1
outer = outer.replace(anchor, '    trace_stage049("setup_begin",child);\n' + anchor, 1)
anchor = '    ssize_t n=readlink(path,expected,sizeof(expected)-1);if(n<=0)return 0;expected[n]=0;'
assert outer.count(anchor) == 1
outer = outer.replace(anchor, '    trace_stage049("namespace_read_begin",child);\n' + anchor + '\n    trace_stage049("namespace_read_end",child);', 1)
anchor = '    DIR *dir=opendir("/proc");if(!dir)return 0;struct dirent *entry;long service=0;'
assert outer.count(anchor) == 1
outer = outer.replace(anchor, '    trace_stage049("process_scan_begin",child);\n' + anchor, 1)
anchor = '    closedir(dir);if(!service)return 0;'
assert outer.count(anchor) == 1
outer = outer.replace(anchor, '    closedir(dir);trace_stage049(service?"service_found":"service_absent",service);if(!service)return 0;', 1)
anchor = '        int fd=open(path,O_RDONLY|O_CLOEXEC);if(fd<0)return -1;'
assert outer.count(anchor) == 1
outer = outer.replace(anchor, '        trace_stage049("instruction_open_begin",i);\n' + anchor + '\n        trace_stage049("instruction_open_end",i);', 1)
anchor = '        ssize_t got=pread(fd,&instruction,sizeof(instruction),(off_t)s->offset);close(fd);'
assert outer.count(anchor) == 1
outer = outer.replace(anchor, anchor + '\n        trace_stage049("instruction_read_end",i);', 1)
anchor = '    mkdir("/sys/kernel/tracing",0755);'
assert outer.count(anchor) == 1
outer = outer.replace(anchor, '    trace_stage049("elf_validation_end",service);\n' + anchor + '\n    trace_stage049("tracefs_mount_begin",service);', 1)
anchor = '    if(mount("tracefs","/sys/kernel/tracing","tracefs",MS_NOSUID|MS_NODEV|MS_NOEXEC,NULL) && errno!=EBUSY)return -1;'
assert outer.count(anchor) == 1
outer = outer.replace(anchor, anchor + '\n    trace_stage049("tracefs_mount_end",service);\n    trace_stage049("existing_events_read_begin",service);', 1)
anchor = '    if(read_text("/sys/kernel/tracing/uprobe_events",text,sizeof(text)))return -1;'
assert outer.count(anchor) == 1
outer = outer.replace(anchor, anchor + '\n    trace_stage049("existing_events_read_end",service);', 1)
anchor = 'native_diagnostics(child);commercial_trace046(child,0);snapshot();'
assert outer.count(anchor) == 1
outer = outer.replace(anchor, 'trace_stage049("diagnostics_begin",i);native_diagnostics(child);trace_stage049("diagnostics_end",i);commercial_trace046(child,0);snapshot();', 1)
payload = p['payload'].replace('outer=' + repr(p['outer']), 'outer=' + repr(outer), 1)
payload = payload.replace('commercial61-native-048', 'commercial61-native-049')
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
