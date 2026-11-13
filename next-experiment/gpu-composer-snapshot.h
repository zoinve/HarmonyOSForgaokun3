/* Read-only diagnostic for the preserved, symbol-inspected Composer binary. */
static void gpu899_composer_snapshot(void)
{
    DIR *dir=opendir("/proc"); if(!dir)return;
    struct dirent *de;
    while((de=readdir(dir))) {
        if(de->d_name[0]<'0'||de->d_name[0]>'9')continue;
        char path[256],comm[128]={0},line[1024];
        snprintf(path,sizeof(path),"/proc/%.32s/comm",de->d_name);
        FILE *fp=fopen(path,"r");if(!fp)continue;
        if(!fgets(comm,sizeof(comm),fp)){fclose(fp);continue;}fclose(fp);
        if(!strstr(comm,"composer"))continue;
        snprintf(path,sizeof(path),"/proc/%.32s/maps",de->d_name);
        fp=fopen(path,"r");if(!fp)continue;
        unsigned long base=0;
        while(fgets(line,sizeof(line),fp)) {
            unsigned long start,end,offset;char perms[8];
            if(strstr(line,"/vendor/lib64/l410-graphics/composer/libdisplay_composer_vdi_impl.z.so")&&
               sscanf(line,"%lx-%lx %7s %lx",&start,&end,perms,&offset)==4&&offset==0)base=start;
        }
        fclose(fp);if(!base)continue;
        snprintf(path,sizeof(path),"/proc/%.32s/mem",de->d_name);
        int fd=open(path,O_RDONLY|O_CLOEXEC);if(fd<0){printf("GPU899_MEM pid=%s errno=%d\n",de->d_name,errno);continue;}
        unsigned char state[1024];ssize_t got=pread(fd,state,sizeof(state),(off_t)(base+0x200b0));
        unsigned counters[24]={0};ssize_t stats=pread(fd,counters,sizeof(counters),(off_t)(base+0x20518));close(fd);
        if(got!=(ssize_t)sizeof(state))continue;
        int client[5],fbfd;unsigned width,height,stride;unsigned long map;
        memcpy(client,state+248,sizeof(client));memcpy(&fbfd,state+848,4);memcpy(&map,state+856,8);
        memcpy(&width,state+968,4);memcpy(&height,state+972,4);memcpy(&stride,state+936,4);
        printf("GPU899_COMPOSER pid=%s client_fd=%d width=%d height=%d stride=%d format=%d fbfd=%d fbmap=%lx fbsize=%ux%u fbstride=%u stats_bytes=%zd\n",de->d_name,client[0],client[1],client[2],client[3],client[4],fbfd,map,width,height,stride,stats);
        printf("GPU899_COUNTERS");for(unsigned i=0;i<24;i++)printf(" %u",counters[i]);puts("");
        if(client[0]>=0&&client[1]>0&&client[1]<=4096&&client[2]>0&&client[2]<=4096&&client[3]>0&&client[3]<=32768) {
            snprintf(path,sizeof(path),"/proc/%.32s/fd/%d",de->d_name,client[0]);
            fd=open(path,O_RDONLY|O_CLOEXEC);if(fd<0){printf("GPU899_CLIENT_OPEN errno=%d\n",errno);continue;}
            unsigned char pixels[4096];got=pread(fd,pixels,sizeof(pixels),0);int saved=errno;close(fd);unsigned nonzero=0;
            for(ssize_t i=0;i<got;i++)if(pixels[i])nonzero++;
            printf("GPU899_CLIENT_SAMPLE bytes=%zd nonzero=%u errno=%d\n",got,nonzero,saved);
        }
    }
    closedir(dir);
}
