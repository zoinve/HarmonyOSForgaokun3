"""Verify actual backing mappings by full content, not overlay synthetic identity."""
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
RESOLVER = r'''
static int hw050_files_equal(int first,int second)
{
    struct stat a,b;
    if(fstat(first,&a) || fstat(second,&b) || !S_ISREG(a.st_mode) || !S_ISREG(b.st_mode) || a.st_size!=b.st_size || a.st_size<0 || a.st_size>64*1024*1024)return 0;
    unsigned char left[16384],right[16384];off_t position=0;
    while(position<a.st_size){
        size_t count=(size_t)(a.st_size-position);if(count>sizeof(left))count=sizeof(left);
        ssize_t x=pread(first,left,count,position),y=pread(second,right,count,position);
        if(x!=(ssize_t)count || y!=(ssize_t)count || memcmp(left,right,count))return 0;
        position+=(off_t)count;
    }
    return 1;
}

static int hw050_resolve(pid_t service)
{
    char path[256],line[1024];
    for(unsigned i=0;i<HW050_EVENTS;++i){
        const struct hw050_spec *spec=&hw050_specs[i];struct stat source;uint32_t instruction=0;
        snprintf(path,sizeof(path),"/proc/%d/root/system/lib64/%s",service,spec->library);
        int fd=open(path,O_RDONLY|O_CLOEXEC);if(fd<0)return -1;
        int status=fstat(fd,&source);ssize_t got=pread(fd,&instruction,sizeof(instruction),(off_t)spec->offset);
        if(status || got!=sizeof(instruction) || instruction!=spec->instruction){close(fd);errno=ENOEXEC;return -1;}
        snprintf(path,sizeof(path),"/proc/%d/maps",service);FILE *maps=fopen(path,"r");
        if(!maps){int error=errno;close(fd);errno=error;return -1;}
        uint64_t address=0;int failure=EAGAIN;
        while(fgets(line,sizeof(line),maps)){
            unsigned long long begin,end,offset,inode;unsigned device_major,device_minor;char permissions[5]={0};
            if(sscanf(line,"%llx-%llx %4s %llx %x:%x %llu",&begin,&end,permissions,&offset,&device_major,&device_minor,&inode)!=7)continue;
            if(!strchr(permissions,'x') || !strstr(line,spec->library) || offset>spec->offset || spec->offset+4-offset>end-begin)continue;
            dprintf(1,"COMMERCIAL051_HW_MAP_CANDIDATE event=%s path_inode=%llu path_dev=%x:%x mapped_inode=%llu mapped_dev=%x:%x begin=0x%llx end=0x%llx file_offset=0x%llx\n",spec->name,(unsigned long long)source.st_ino,major(source.st_dev),minor(source.st_dev),inode,device_major,device_minor,begin,end,offset);
            snprintf(path,sizeof(path),"/proc/%d/map_files/%llx-%llx",service,begin,end);
            int mapped=open(path,O_RDONLY|O_CLOEXEC);if(mapped<0){failure=errno;dprintf(1,"COMMERCIAL051_HW_MAP_FILE_REJECTED event=%s errno=%d\n",spec->name,failure);continue;}
            struct stat actual;int valid=!fstat(mapped,&actual) && S_ISREG(actual.st_mode) && inode==(unsigned long long)actual.st_ino && device_major==major(actual.st_dev) && device_minor==minor(actual.st_dev);
            int equal=valid && hw050_files_equal(fd,mapped);close(mapped);
            if(!equal){failure=ENOEXEC;dprintf(1,"COMMERCIAL051_HW_MAP_FILE_REJECTED event=%s identity_valid=%d full_bytes_equal=0 errno=%d\n",spec->name,valid,failure);continue;}
            address=begin+spec->offset-offset;break;
        }
        fclose(maps);close(fd);if(!address){errno=failure;return -1;}
        hw050_addresses[i]=address;
        dprintf(1,"COMMERCIAL051_HW_ADDRESS event=%s global_pid=%d address=0x%llx file_offset=0x%llx instruction_matched=1 executable_inode_matched=1 mapped_file_full_bytes_matched=1\n",spec->name,service,(unsigned long long)address,(unsigned long long)spec->offset);
    }
    return 0;
}
'''


def replace_resolver(source):
    header = (BASE / 'next-experiment/commercial-hwbreak-050.h').read_text()
    old = header[header.index('static int hw050_resolve('):header.index('static void hw050_attach(')]
    assert source.count(old) == 1
    return source.replace(old, RESOLVER + '\n', 1).replace('COMMERCIAL050_HW', 'COMMERCIAL051_HW')
