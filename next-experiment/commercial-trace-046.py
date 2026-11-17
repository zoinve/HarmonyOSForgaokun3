"""Bounded target-only original-service tracing, with no object layout reads."""
from pathlib import Path
import json

BASE = Path(__file__).resolve().parents[1]
HELPER = r'''
struct trace_spec046 {const char *event,*library,*arguments;unsigned long long offset;unsigned instruction;int returns;};
static const struct trace_spec046 trace_specs046[]={SPECS046};
static int trace_state046;
static int trace_write046(const char *path,const char *text)
{
    int fd=open(path,O_WRONLY|O_CLOEXEC);if(fd<0)return -1;
    size_t n=strlen(text),done=0;unsigned retries=0;int error=0;
    while(done<n){ssize_t count=write(fd,text+done,n-done);
        if(count<0 && errno==EINTR && ++retries<4)continue;
        if(count<=0){error=errno?errno:EIO;break;}done+=(size_t)count;
    }
    close(fd);if(error){errno=error;return -1;}return 0;
}
static int trace_setup046(pid_t child)
{
    char path[256],expected[128]={},actual[128]={},text[4096],root[128];
    snprintf(path,sizeof(path),"/proc/%d/ns/pid",child);
    ssize_t n=readlink(path,expected,sizeof(expected)-1);if(n<=0)return 0;expected[n]=0;
    DIR *dir=opendir("/proc");if(!dir)return 0;struct dirent *entry;long service=0;
    while((entry=readdir(dir))){char *end;long pid=strtol(entry->d_name,&end,10);
        if(!*entry->d_name || *end || pid<=0)continue;
        snprintf(path,sizeof(path),"/proc/%ld/cmdline",pid);
        if(read_text(path,text,sizeof(text)) || !strstr(text,"/system/bin/render_service"))continue;
        snprintf(path,sizeof(path),"/proc/%ld/ns/pid",pid);
        n=readlink(path,actual,sizeof(actual)-1);if(n<=0)continue;actual[n]=0;
        if(!strcmp(expected,actual)){service=pid;break;}
    }
    closedir(dir);if(!service)return 0;
    snprintf(root,sizeof(root),"/proc/%ld/root",service);
    for(unsigned i=0;i<sizeof(trace_specs046)/sizeof(trace_specs046[0]);++i){
        const struct trace_spec046 *s=&trace_specs046[i];unsigned instruction=0;
        snprintf(path,sizeof(path),"%s/system/lib64/%s",root,s->library);
        int fd=open(path,O_RDONLY|O_CLOEXEC);if(fd<0)return -1;
        ssize_t got=pread(fd,&instruction,sizeof(instruction),(off_t)s->offset);close(fd);
        if(got!=sizeof(instruction) || instruction!=s->instruction){errno=ENOEXEC;return -1;}
    }
    mkdir("/sys/kernel/tracing",0755);
    if(mount("tracefs","/sys/kernel/tracing","tracefs",MS_NOSUID|MS_NODEV|MS_NOEXEC,NULL) && errno!=EBUSY)return -1;
    if(read_text("/sys/kernel/tracing/uprobe_events",text,sizeof(text)))return -1;
    if(strspn(text," \n\r\t")!=strlen(text)){errno=EBUSY;return -1;}
    if(trace_write046("/sys/kernel/tracing/tracing_on","0\n") ||
       trace_write046("/sys/kernel/tracing/current_tracer","nop\n") ||
       trace_write046("/sys/kernel/tracing/buffer_size_kb","128\n") ||
       trace_write046("/sys/kernel/tracing/trace_clock","mono\n"))return -1;
    for(unsigned i=0;i<sizeof(trace_specs046)/sizeof(trace_specs046[0]);++i){
        const struct trace_spec046 *s=&trace_specs046[i];
        snprintf(text,sizeof(text),"p:commercial046/%s %s/system/lib64/%s:0x%llx %s\n",s->event,root,s->library,s->offset,s->arguments);
        if(trace_write046("/sys/kernel/tracing/uprobe_events",text))return -1;
        if(s->returns){
            snprintf(text,sizeof(text),"r:commercial046/%s_return %s/system/lib64/%s:0x%llx value=$retval:x64\n",s->event,root,s->library,s->offset);
            if(trace_write046("/sys/kernel/tracing/uprobe_events",text))return -1;
        }
    }
    if(trace_write046("/sys/kernel/tracing/events/commercial046/enable","1\n") ||
       trace_write046("/sys/kernel/tracing/tracing_on","1\n"))return -1;
    dprintf(1,"COMMERCIAL046_TRACE_READY global_pid=%ld namespace=%s register_arguments_only=1 file_instructions_matched=1\n",service,expected);
    commercial_outer_stream044("/sys/kernel/tracing/uprobe_events",32768);
    return 1;
}
static void commercial_trace046(pid_t child,int final)
{
    int saved=errno;
    if(!trace_state046 && !final){
        int result=trace_setup046(child),error=errno;
        if(result<0){trace_state046=-1;
            (void)trace_write046("/sys/kernel/tracing/events/commercial046/enable","0\n");
            dprintf(1,"COMMERCIAL046_TRACE_SETUP_FAILED errno=%d original_service_continues=1\n",error);
        }else if(result>0)trace_state046=1;
    }
    if(trace_state046==1){
        dprintf(1,"COMMERCIAL046_TRACE_SAMPLE final=%d truncated_streams_do_not_prove_absence=1\n",final);
        commercial_outer_stream044("/sys/kernel/tracing/trace",1048576);
        commercial_outer_stream044("/sys/kernel/tracing/uprobe_profile",32768);
        if(final){
            (void)trace_write046("/sys/kernel/tracing/events/commercial046/enable","0\n");
            (void)trace_write046("/sys/kernel/tracing/tracing_on","0\n");
        }
    }
    errno=saved;
}
'''


def instrument(source):
    audit = json.loads((BASE / 'reports/commercial-trace-audit-046/result.json').read_text())
    assert audit['original_elf_hashes_verified'] and audit['executable_offsets_verified']
    specs = []
    for row in audit['probes']:
        args = row['definition'].split(' ', 2)
        arguments = args[2] if len(args) == 3 else ''
        specs.append('{' + ','.join([json.dumps(row['event']), json.dumps(row['library']),
            json.dumps(arguments), row['file_offset'] + 'ULL',
            hex(int.from_bytes(bytes.fromhex(row['original_instruction']), 'little')) + 'u',
            str(int('return_definition' in row))]) + '}')
    anchor = 'static void native_original(void)'
    assert source.count(anchor) == 1
    source = source.replace(anchor, HELPER.replace('SPECS046', ',\n'.join(specs)) + '\n' + anchor, 1)
    early = 'native_diagnostics(child);snapshot();if(got==child)break;sleep(5);'
    assert source.count(early) == 1
    source = source.replace(early, 'native_diagnostics(child);commercial_trace046(child,0);snapshot();if(got==child)break;sleep(5);', 1)
    late = 'commercial_outer_binder044(child);snapshot();'
    assert source.count(late) == 1
    source = source.replace(late, 'commercial_outer_binder044(child);commercial_trace046(child,0);snapshot();', 1)
    end = '            if(got==0){'
    assert source.count(end) == 1
    return source.replace(end, '            commercial_trace046(child,1);\n' + end, 1)
