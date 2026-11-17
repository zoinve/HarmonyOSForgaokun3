static int event086_read(void)
{
    const char *root="/data/log/eventlog";
    int fd=open(root,O_RDONLY|O_DIRECTORY|O_CLOEXEC|O_NOFOLLOW);
    if(fd<0){dprintf(1,"EVENT086_DIRECTORY_MISSING errno=%d\n",errno);return 88;}
    DIR *dir=fdopendir(fd);
    if(!dir){close(fd);return 89;}
    unsigned scanned=0,files=0;
    struct dirent *entry;
    while(scanned<256 && files<4 && (entry=readdir(dir))){
        ++scanned;
        size_t length=strlen(entry->d_name);
        if(strncmp(entry->d_name,"THREAD_BLOCK_",13) || length<4 ||
           strcmp(entry->d_name+length-4,".log"))continue;
        int item=openat(dirfd(dir),entry->d_name,O_RDONLY|O_CLOEXEC|O_NOFOLLOW);
        if(item<0)continue;
        struct stat st;
        if(fstat(item,&st) || !S_ISREG(st.st_mode)){close(item);continue;}
        ++files;
        dprintf(1,"EVENT086_FILE_BEGIN name=%s size=%lld\n",entry->d_name,(long long)st.st_size);
        char data[4096];unsigned bytes=0;int error=0,eof=0;
        while(bytes<1048576){
            ssize_t n=read(item,data,sizeof(data));
            if(n<0 && errno==EINTR)continue;
            if(n<0){error=errno;break;}
            if(!n){eof=1;break;}
            ssize_t offset=0;
            while(offset<n){
                ssize_t count=write(1,data+offset,(size_t)(n-offset));
                if(count<0 && errno==EINTR)continue;
                if(count<=0){error=count<0 ? errno : EIO;break;}
                offset+=count;
            }
            bytes+=(unsigned)offset;
            if(error)break;
        }
        close(item);
        dprintf(1,"\nEVENT086_FILE_END name=%s bytes=%u eof=%d errno=%d full_file_not_inferred=1\n",
                entry->d_name,bytes,eof,error);
    }
    closedir(dir);
    dprintf(1,"EVENT086_SUMMARY entries=%u files=%u bounded=1\n",scanned,files);
    return 0;
}
