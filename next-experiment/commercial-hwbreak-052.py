"""Validate actual executable bytes without equating overlay and backing inodes."""
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
RESOLVER = r'''
static int hw052_mapping_equal(int file,int memory,uint64_t begin,uint64_t offset,uint64_t length)
{
    struct stat info;
    if(fstat(file,&info))return 0;
    if(!S_ISREG(info.st_mode) || info.st_size<0 || !length || length>64*1024*1024 ||
       offset>(uint64_t)info.st_size || length>(uint64_t)info.st_size-offset ||
       begin>INT64_MAX || length>(uint64_t)INT64_MAX-begin){errno=EINVAL;return 0;}
    unsigned char disk[16384],live[16384];uint64_t position=0;
    while(position<length){
        size_t count=(size_t)(length-position);if(count>sizeof(disk))count=sizeof(disk);
        ssize_t a=pread(file,disk,count,(off_t)(offset+position));
        if(a!=(ssize_t)count){if(a>=0)errno=EIO;return 0;}
        ssize_t b=pread(memory,live,count,(off_t)(begin+position));
        if(b!=(ssize_t)count){if(b>=0)errno=EIO;return 0;}
        if(memcmp(disk,live,count)){errno=ENOEXEC;return 0;}
        position+=count;
    }
    return 1;
}

static int hw052_mapping_unchanged(pid_t service,const char *expected)
{
    char path[128],line[1024];snprintf(path,sizeof(path),"/proc/%d/maps",service);
    FILE *maps=fopen(path,"r");if(!maps)return 0;
    int found=0;while(fgets(line,sizeof(line),maps))if(!strcmp(line,expected)){found=1;break;}
    fclose(maps);if(!found)errno=EAGAIN;return found;
}

static int hw050_resolve(pid_t service)
{
    char path[512],line[1024];
    for(unsigned i=0;i<HW050_EVENTS;++i){
        const struct hw050_spec *spec=&hw050_specs[i];uint32_t instruction=0;
        snprintf(path,sizeof(path),"/proc/%d/root/system/lib64/%s",service,spec->library);
        int file=open(path,O_RDONLY|O_CLOEXEC);if(file<0)return -1;
        ssize_t got=pread(file,&instruction,sizeof(instruction),(off_t)spec->offset);
        if(got!=sizeof(instruction) || instruction!=spec->instruction){close(file);errno=ENOEXEC;return -1;}
        snprintf(path,sizeof(path),"/proc/%d/mem",service);
        int memory=open(path,O_RDONLY|O_CLOEXEC);if(memory<0){int error=errno;close(file);errno=error;return -1;}
        snprintf(path,sizeof(path),"/proc/%d/maps",service);FILE *maps=fopen(path,"r");
        if(!maps){int error=errno;close(memory);close(file);errno=error;return -1;}
        char expected[512];snprintf(expected,sizeof(expected),"/system/lib64/%s",spec->library);
        uint64_t address=0;int failure=EAGAIN;
        while(fgets(line,sizeof(line),maps)){
            unsigned long long begin,end,offset,inode;unsigned device_major,device_minor;char permissions[5]={0};int consumed=0;
            if(sscanf(line,"%llx-%llx %4s %llx %x:%x %llu %n",&begin,&end,permissions,&offset,&device_major,&device_minor,&inode,&consumed)!=7 || !consumed)continue;
            const char *name=line+consumed;size_t size=strcspn(name,"\n");
            if(strlen(expected)!=size || strncmp(name,expected,size) || !strchr(permissions,'r') ||
               !strchr(permissions,'x') || strchr(permissions,'w') || begin>=end || offset>spec->offset ||
               end-begin<4 || spec->offset-offset>end-begin-4)continue;
            dprintf(1,"COMMERCIAL052_HW_MAP_CANDIDATE event=%s mapped_inode=%llu mapped_dev=%x:%x begin=0x%llx end=0x%llx file_offset=0x%llx\n",spec->name,inode,device_major,device_minor,begin,end,offset);
            int equal=hw052_mapping_equal(file,memory,begin,offset,end-begin);int error=errno;
            if(!equal){failure=error;dprintf(1,"COMMERCIAL052_HW_MEMORY_REJECTED event=%s errno=%d executable_bytes_matched=0\n",spec->name,failure);continue;}
            if(!hw052_mapping_unchanged(service,line)){failure=errno;dprintf(1,"COMMERCIAL052_HW_MAPPING_CHANGED event=%s errno=%d\n",spec->name,failure);continue;}
            address=begin+spec->offset-offset;break;
        }
        fclose(maps);close(memory);close(file);if(!address){errno=failure;return -1;}
        hw050_addresses[i]=address;
        dprintf(1,"COMMERCIAL052_HW_ADDRESS event=%s global_pid=%d address=0x%llx file_offset=0x%llx instruction_matched=1 executable_mapping_full_bytes_matched=1 mapping_record_rechecked=1 memory_read_only=1\n",spec->name,service,(unsigned long long)address,(unsigned long long)spec->offset);
    }
    return 0;
}
'''


def replace_resolver(source):
    header = (BASE / 'next-experiment/commercial-hwbreak-050.h').read_text()
    old = header[header.index('static int hw050_resolve('):header.index('static void hw050_attach(')]
    assert source.count(old) == 1
    return source.replace(old, RESOLVER + '\n', 1).replace('COMMERCIAL050_HW', 'COMMERCIAL052_HW')
