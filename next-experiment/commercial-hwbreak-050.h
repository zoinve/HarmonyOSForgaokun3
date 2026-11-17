#include <stdint.h>
#include <linux/perf_event.h>
#include <linux/hw_breakpoint.h>
#include <sys/mman.h>
#include <sys/ioctl.h>
#include <sys/sysmacros.h>

struct hw050_spec {const char *name,*library;uint64_t offset;uint32_t instruction;};
static const struct hw050_spec hw050_specs[]={HW050_SPECS};
#define HW050_EVENTS 4
#define HW050_SLOTS 256
#define HW050_PAGES 64
struct hw050_event {
    pid_t tid;unsigned spec;int used,fd;void *mapping;size_t length;
    uint64_t samples,lost,other,malformed;
};
static struct hw050_event hw050_events[HW050_SLOTS];
static pid_t hw050_service;
static uint64_t hw050_addresses[HW050_EVENTS];

static void hw050_ring_copy(void *output,const unsigned char *ring,size_t size,uint64_t offset,size_t count)
{
    size_t start=(size_t)(offset%size),first=size-start;
    if(first>count)first=count;
    memcpy(output,ring+start,first);
    if(first<count)memcpy((unsigned char *)output+first,ring,count-first);
}

static void hw050_drain(struct hw050_event *event)
{
    if(event->fd<0 || !event->mapping)return;
    struct perf_event_mmap_page *meta=event->mapping;
    uint64_t head=__atomic_load_n(&meta->data_head,__ATOMIC_ACQUIRE),tail=meta->data_tail;
    size_t offset=(size_t)meta->data_offset,size=(size_t)meta->data_size;
    if(!size || offset>event->length || size>event->length-offset || head<tail || head-tail>size){
        dprintf(1,"COMMERCIAL050_HW_BAD_RING tid=%d event=%s head=%llu tail=%llu size=%zu\n",event->tid,hw050_specs[event->spec].name,(unsigned long long)head,(unsigned long long)tail,size);
        ++event->malformed;return;
    }
    unsigned emitted=0,records=0,suppressed=0;
    const unsigned char *ring=(unsigned char *)event->mapping+offset;
    while(tail<head && records++<4096){
        struct perf_event_header header;
        if(head-tail<sizeof(header)){++event->malformed;break;}
        hw050_ring_copy(&header,ring,size,tail,sizeof(header));
        if(header.size<sizeof(header) || header.size>1024 || header.size>head-tail){++event->malformed;break;}
        unsigned char record[1024];hw050_ring_copy(record,ring,size,tail,header.size);
        if(header.type==PERF_RECORD_SAMPLE){
            uint64_t ip,ns,abi,registers[7];uint32_t ids[2];
            if(header.size<40){++event->malformed;break;}
            memcpy(&ip,record+8,8);memcpy(ids,record+16,8);memcpy(&ns,record+24,8);memcpy(&abi,record+32,8);
            if(abi!=PERF_SAMPLE_REGS_ABI_64 || header.size!=96){
                ++event->malformed;
                dprintf(1,"COMMERCIAL050_HW_BAD_SAMPLE tid=%d event=%s bytes=%u abi=%llu\n",event->tid,hw050_specs[event->spec].name,header.size,(unsigned long long)abi);
            }else{
                memcpy(registers,record+40,sizeof(registers));++event->samples;
                if(emitted++<128){
                    dprintf(1,"COMMERCIAL050_HW_SAMPLE event=%s global_pid=%u global_tid=%u ns=%llu ip=0x%llx ip_matches=%d x0=0x%llx x1=0x%llx x2=0x%llx x3=0x%llx x4=0x%llx x5=0x%llx x6=0x%llx\n",hw050_specs[event->spec].name,ids[0],ids[1],(unsigned long long)ns,(unsigned long long)ip,ip==hw050_addresses[event->spec],(unsigned long long)registers[0],(unsigned long long)registers[1],(unsigned long long)registers[2],(unsigned long long)registers[3],(unsigned long long)registers[4],(unsigned long long)registers[5],(unsigned long long)registers[6]);
                }else ++suppressed;
            }
        }else if(header.type==PERF_RECORD_LOST && header.size>=24){
            uint64_t lost;memcpy(&lost,record+16,8);event->lost+=lost;
        }else if(header.type==PERF_RECORD_LOST_SAMPLES && header.size>=16){
            uint64_t lost;memcpy(&lost,record+8,8);event->lost+=lost;
        }else ++event->other;
        tail+=header.size;
    }
    __atomic_store_n(&meta->data_tail,tail,__ATOMIC_RELEASE);
    uint64_t count=0;ssize_t got=read(event->fd,&count,sizeof(count));
    dprintf(1,"COMMERCIAL050_HW_COUNTS tid=%d event=%s count_valid=%d count=%llu samples=%llu lost=%llu other=%llu malformed=%llu suppressed_this_drain=%u pending_bytes=%llu\n",event->tid,hw050_specs[event->spec].name,got==(ssize_t)sizeof(count),(unsigned long long)count,(unsigned long long)event->samples,(unsigned long long)event->lost,(unsigned long long)event->other,(unsigned long long)event->malformed,suppressed,(unsigned long long)(head-tail));
}

static void hw050_close(struct hw050_event *event)
{
    if(event->fd>=0){(void)ioctl(event->fd,PERF_EVENT_IOC_DISABLE,0);hw050_drain(event);}
    if(event->mapping)munmap(event->mapping,event->length);
    if(event->fd>=0)close(event->fd);
    memset(event,0,sizeof(*event));event->fd=-1;
}

static pid_t hw050_find_service(pid_t child)
{
    char path[128],expected[128],actual[128],command[4096];
    snprintf(path,sizeof(path),"/proc/%d/ns/pid",child);
    ssize_t n=readlink(path,expected,sizeof(expected)-1);if(n<=0)return 0;expected[n]=0;
    DIR *dir=opendir("/proc");if(!dir)return 0;struct dirent *entry;pid_t service=0;
    while((entry=readdir(dir))){char *end;long pid=strtol(entry->d_name,&end,10);
        if(!*entry->d_name || *end || pid<=0)continue;
        snprintf(path,sizeof(path),"/proc/%ld/cmdline",pid);
        if(read_text(path,command,sizeof(command)) || strcmp(command,"/system/bin/render_service"))continue;
        snprintf(path,sizeof(path),"/proc/%ld/ns/pid",pid);
        n=readlink(path,actual,sizeof(actual)-1);if(n<=0)continue;actual[n]=0;
        if(!strcmp(expected,actual)){service=(pid_t)pid;break;}
    }
    closedir(dir);return service;
}

static int hw050_resolve(pid_t service)
{
    char path[256],line[1024];
    for(unsigned i=0;i<HW050_EVENTS;++i){
        const struct hw050_spec *spec=&hw050_specs[i];struct stat info;uint32_t instruction=0;
        snprintf(path,sizeof(path),"/proc/%d/root/system/lib64/%s",service,spec->library);
        int fd=open(path,O_RDONLY|O_CLOEXEC);if(fd<0)return -1;
        int status=fstat(fd,&info);ssize_t got=pread(fd,&instruction,sizeof(instruction),(off_t)spec->offset);close(fd);
        if(status || got!=sizeof(instruction) || instruction!=spec->instruction){errno=ENOEXEC;return -1;}
        snprintf(path,sizeof(path),"/proc/%d/maps",service);FILE *maps=fopen(path,"r");if(!maps)return -1;
        uint64_t address=0;
        while(fgets(line,sizeof(line),maps)){
            unsigned long long begin,end,offset,inode;unsigned device_major,device_minor;char permissions[5]={0};
            if(sscanf(line,"%llx-%llx %4s %llx %x:%x %llu",&begin,&end,permissions,&offset,&device_major,&device_minor,&inode)!=7)continue;
            if(!strchr(permissions,'x') || inode!=(unsigned long long)info.st_ino || device_major!=major(info.st_dev) || device_minor!=minor(info.st_dev))continue;
            if(offset<=spec->offset && spec->offset+4-offset<=end-begin){address=begin+spec->offset-offset;break;}
        }
        fclose(maps);if(!address){errno=EAGAIN;return -1;}
        hw050_addresses[i]=address;
        dprintf(1,"COMMERCIAL050_HW_ADDRESS event=%s global_pid=%d address=0x%llx file_offset=0x%llx instruction_matched=1 executable_inode_matched=1\n",spec->name,service,(unsigned long long)address,(unsigned long long)spec->offset);
    }
    return 0;
}

static void hw050_attach(pid_t service)
{
    char path[128];snprintf(path,sizeof(path),"/proc/%d/task",service);
    DIR *tasks=opendir(path);if(!tasks)return;struct dirent *entry;
    while((entry=readdir(tasks))){char *end;long tid=strtol(entry->d_name,&end,10);
        if(!*entry->d_name || *end || tid<=0)continue;
        for(unsigned spec=0;spec<HW050_EVENTS;++spec){
            struct hw050_event *event=NULL;int exists=0;
            for(unsigned j=0;j<HW050_SLOTS;++j){
                if(hw050_events[j].used && hw050_events[j].tid==tid && hw050_events[j].spec==spec){exists=1;break;}
                if(!hw050_events[j].used && !event)event=&hw050_events[j];
            }
            if(exists)continue;
            if(!event){dprintf(1,"COMMERCIAL050_HW_SLOT_LIMIT global_pid=%d tid=%ld\n",service,tid);closedir(tasks);return;}
            memset(event,0,sizeof(*event));event->used=1;event->tid=(pid_t)tid;event->spec=spec;event->fd=-1;
            struct perf_event_attr attr={0};attr.type=PERF_TYPE_BREAKPOINT;attr.size=sizeof(attr);
            attr.bp_type=HW_BREAKPOINT_X;attr.bp_addr=hw050_addresses[spec];attr.bp_len=HW_BREAKPOINT_LEN_4;
            attr.sample_period=1;attr.sample_type=PERF_SAMPLE_IP|PERF_SAMPLE_TID|PERF_SAMPLE_TIME|PERF_SAMPLE_REGS_USER;
            attr.sample_regs_user=0x7f;attr.disabled=1;attr.exclude_kernel=1;attr.exclude_hv=1;
            attr.wakeup_events=1;attr.use_clockid=1;attr.clockid=CLOCK_MONOTONIC;
            int fd=(int)syscall(__NR_perf_event_open,&attr,(pid_t)tid,-1,-1,PERF_FLAG_FD_CLOEXEC);
            if(fd<0){dprintf(1,"COMMERCIAL050_HW_ATTACH_FAILED tid=%ld event=%s errno=%d\n",tid,hw050_specs[spec].name,errno);continue;}
            long page=sysconf(_SC_PAGESIZE);size_t length=(HW050_PAGES+1)*(size_t)page;
            void *mapping=mmap(NULL,length,PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);
            if(mapping==MAP_FAILED){int error=errno;close(fd);dprintf(1,"COMMERCIAL050_HW_MMAP_FAILED tid=%ld event=%s errno=%d\n",tid,hw050_specs[spec].name,error);continue;}
            event->fd=fd;event->mapping=mapping;event->length=length;
            if(ioctl(fd,PERF_EVENT_IOC_ENABLE,0)){int error=errno;hw050_close(event);event->used=1;event->tid=(pid_t)tid;event->spec=spec;dprintf(1,"COMMERCIAL050_HW_ENABLE_FAILED tid=%ld event=%s errno=%d\n",tid,hw050_specs[spec].name,error);continue;}
            dprintf(1,"COMMERCIAL050_HW_ATTACHED global_pid=%d global_tid=%ld event=%s fd=%d ring_bytes=%zu registers_only=1 instruction_replacement=0\n",service,tid,hw050_specs[spec].name,fd,length);
        }
    }
    closedir(tasks);
}

static void hw050_tick(pid_t child,int final)
{
    int saved=errno;
    if(final){
        for(unsigned i=0;i<HW050_SLOTS;++i)if(hw050_events[i].used)hw050_close(&hw050_events[i]);
        dprintf(1,"COMMERCIAL050_HW_STOPPED original_service_unmodified=1\n");errno=saved;return;
    }
    pid_t service=hw050_find_service(child);
    if(service && service!=hw050_service){
        for(unsigned i=0;i<HW050_SLOTS;++i)if(hw050_events[i].used)hw050_close(&hw050_events[i]);
        memset(hw050_addresses,0,sizeof(hw050_addresses));
        dprintf(1,"COMMERCIAL050_HW_SETUP_BEGIN global_pid=%d child=%d\n",service,child);snapshot();
        if(hw050_resolve(service)){dprintf(1,"COMMERCIAL050_HW_MAPPING_WAIT global_pid=%d errno=%d\n",service,errno);errno=saved;return;}
        hw050_service=service;
    }
    if(service){
        for(unsigned i=0;i<HW050_SLOTS;++i)if(hw050_events[i].used){
            char path[128];snprintf(path,sizeof(path),"/proc/%d/task/%d",service,hw050_events[i].tid);
            if(access(path,F_OK))hw050_close(&hw050_events[i]);
        }
        hw050_attach(service);
    }else dprintf(1,"COMMERCIAL050_HW_WAIT_SERVICE child=%d\n",child);
    for(unsigned i=0;i<HW050_SLOTS;++i)if(hw050_events[i].used)hw050_drain(&hw050_events[i]);
    errno=saved;
}
