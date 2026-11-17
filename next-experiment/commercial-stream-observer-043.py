"""Read complete bounded seq-files in the isolated target, not single-read maps."""
HELPER = r'''
static void commercial_stream043(const char *path,unsigned sample,long pid,unsigned limit)
{
    int saved=errno,fd=open(path,O_RDONLY|O_CLOEXEC),error=0;
    unsigned total=0;int eof=0;
    dprintf(commercial_diag_fd003,"COMMERCIAL043_STREAM_BEGIN sample=%u pid=%ld path=%s limit=%u\n",sample,pid,path,limit);
    if(fd<0)error=errno;
    else {
        char buffer[4096];unsigned interrupted=0;
        while(total<limit){
            size_t wanted=limit-total;if(wanted>sizeof(buffer))wanted=sizeof(buffer);
            ssize_t count=read(fd,buffer,wanted);
            if(count<0){if(errno==EINTR && ++interrupted<4)continue;error=errno;break;}
            if(!count){eof=1;break;}
            interrupted=0;
            if(dprintf(commercial_diag_fd003,"%.*s",(int)count,buffer)<0){error=errno;break;}
            total+=(unsigned)count;
        }
        if(total==limit){char extra;ssize_t count=read(fd,&extra,1);if(!count)eof=1;else if(count<0)error=errno;}
        close(fd);
    }
    dprintf(commercial_diag_fd003,"\nCOMMERCIAL043_STREAM_END sample=%u pid=%ld path=%s bytes=%u eof=%d errno=%d\n",sample,pid,path,total,eof,error);
    errno=saved;
}
static void commercial_binder_debug043(unsigned sample)
{
    if(sample!=15 && sample!=17 && sample!=20 && sample!=24 && sample!=28)return;
    if(sample==15){
        struct stat st;
        if(stat("/sys/kernel/debug/binder/transaction_log",&st)){
            mkdir("/sys/kernel/debug",0755);errno=0;
            int result=mount("debugfs","/sys/kernel/debug","debugfs",MS_NOSUID|MS_NODEV|MS_NOEXEC,NULL);
            int error=errno;
            dprintf(commercial_diag_fd003,"COMMERCIAL043_DEBUGFS result=%d errno=%d target_only=1\n",result,error);
        }
    }
    commercial_stream043("/sys/kernel/debug/binder/transaction_log",sample,0,65536);
    commercial_stream043("/sys/kernel/debug/binder/failed_transaction_log",sample,0,65536);
}
'''


def instrument(source):
    anchor = 'static void commercial_tasks039(unsigned sample)'
    assert source.count(anchor) == 1
    source = source.replace(anchor, HELPER + '\n' + anchor, 1)
    old = '''            char maps[32768];snprintf(path,sizeof(path),"/proc/%ld/maps",pid);
            ssize_t count=read_path(path,maps,sizeof(maps));
            if(count>0)dprintf(commercial_diag_fd003,"COMMERCIAL039_MAPS pid=%ld bytes=%zd\\n%s\\n",pid,count,maps);'''
    new = '''            snprintf(path,sizeof(path),"/proc/%ld/maps",pid);
            commercial_stream043(path,sample,pid,1048576);'''
    assert source.count(old) == 1
    source = source.replace(old, new, 1)
    old = '        snprintf(path,sizeof(path),"/proc/%ld/task",pid);'
    new = '''        snprintf(path,sizeof(path),"/sys/kernel/debug/binder/proc/%ld",pid);
        commercial_stream043(path,sample,pid,65536);
''' + old
    assert source.count(old) == 1
    source = source.replace(old, new, 1)
    call = '        commercial_tasks039(sample);'
    assert source.count(call) == 1
    return source.replace(call, '        commercial_binder_debug043(sample);\n' + call, 1)
