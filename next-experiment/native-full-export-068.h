/* Copy only immutable, completely published diagnostic images to the run FD. */
#pragma once
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

struct full068_export_context { int source,dest; uid_t owner; };

static int full068_put(int fd,const void *data,size_t size){
 const unsigned char *p=(const unsigned char *)data;
 while(size){
  ssize_t n=write(fd,p,size);
  if(n<0 && errno==EINTR)continue;
  if(n<=0)return -1;
  p+=n;size-=(size_t)n;
 }
 return 0;
}

static int full068_same(const struct stat *a,const struct stat *b){
 return a->st_dev==b->st_dev && a->st_ino==b->st_ino &&
  a->st_size==b->st_size && a->st_uid==b->st_uid && a->st_mode==b->st_mode &&
  a->st_nlink==b->st_nlink && a->st_mtim.tv_sec==b->st_mtim.tv_sec &&
  a->st_mtim.tv_nsec==b->st_mtim.tv_nsec && a->st_ctim.tv_sec==b->st_ctim.tv_sec &&
  a->st_ctim.tv_nsec==b->st_ctim.tv_nsec;
}

static int full068_copy(const struct full068_export_context *ctx,const char *name,
                        const char *dest,uint64_t expected){
 if(!expected || expected>16*1024*1024ULL+128)return -1;
 int input=openat(ctx->source,name,O_RDONLY|O_NOFOLLOW|O_CLOEXEC);
 if(input<0)return -1;
 struct stat before,after;
 int good=!fstat(input,&before) && S_ISREG(before.st_mode) && before.st_nlink==1 &&
  before.st_uid==ctx->owner && before.st_size==(off_t)expected;
 char temporary[96];int length=snprintf(temporary,sizeof(temporary),"%s.part",dest);
 int output=-1;
 if(good && length>0 && (size_t)length<sizeof(temporary))
  output=openat(ctx->dest,temporary,O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);
 good=good && output>=0;
 unsigned char buffer[65536];uint64_t copied=0;
 while(good && copied<expected){
  size_t want=expected-copied<sizeof(buffer)?(size_t)(expected-copied):sizeof(buffer);
  ssize_t n=read(input,buffer,want);
  if(n<0 && errno==EINTR)continue;
  if(n<=0 || full068_put(output,buffer,(size_t)n)){good=0;break;}
  copied+=(uint64_t)n;
 }
 if(good){
  ssize_t extra;do{extra=read(input,buffer,1);}while(extra<0 && errno==EINTR);
  good=extra==0 && copied==expected && !fstat(input,&after) && full068_same(&before,&after);
 }
 if(close(input))good=0;
 if(output>=0){if(good && fsync(output))good=0;if(close(output))good=0;}
 if(good && linkat(ctx->dest,temporary,ctx->dest,dest,0))good=0;
 if(good && unlinkat(ctx->dest,temporary,0))good=0;
 return good?0:-1;
}

static void full068_export_worker(void *argument){
 const struct full068_export_context *ctx=(const struct full068_export_context *)argument;
 struct stat directory,marker;
 if(fstat(ctx->source,&directory) || !S_ISDIR(directory.st_mode) ||
    directory.st_uid!=ctx->owner || (directory.st_mode&0777)!=0700)_exit(126);
 int fd=openat(ctx->source,"ready",O_RDONLY|O_NOFOLLOW|O_CLOEXEC);
 if(fd<0 || fstat(fd,&marker) || !S_ISREG(marker.st_mode) || marker.st_nlink!=1 ||
    marker.st_uid!=ctx->owner || marker.st_size<=0 || marker.st_size>=256)_exit(126);
 char text[256];size_t used=0;
 while(used<(size_t)marker.st_size){
  ssize_t n=read(fd,text+used,(size_t)marker.st_size-used);
  if(n<0 && errno==EINTR)continue;
  if(n<=0)_exit(126);
  used+=(size_t)n;
 }
 struct stat after;
 if(read(fd,text+used,1)!=0 || fstat(fd,&after) || !full068_same(&marker,&after) || close(fd))_exit(126);
 text[used]=0;
 unsigned long long source_bytes=0,output_bytes=0,mono_us=0;unsigned fb=0;int consumed=0;
 if(sscanf(text,"FULL068_READY source_bytes=%llu output_bytes=%llu mono_us=%llu fb=%u\n%n",
   &source_bytes,&output_bytes,&mono_us,&fb,&consumed)!=4 || consumed!=(int)used ||
   used!=strlen(text) || mono_us<120000000 || mono_us>=145000000 || !fb)_exit(126);
 if(full068_copy(ctx,"source.ppm","full-source-068.ppm",source_bytes) ||
    full068_copy(ctx,"output.ppm","full-output-068.ppm",output_bytes))_exit(126);
 int out=openat(ctx->dest,"full-ready-068",O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);
 if(out<0 || full068_put(out,text,used) || fsync(out) || close(out) || fsync(ctx->dest))_exit(126);
}
