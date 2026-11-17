/* Read-only, full-resolution observations of caller-synchronized pixel maps. */
#pragma once
#include <cerrno>
#include <cstdint>
#include <cstdio>
#include <fcntl.h>
#include <unistd.h>

struct Full068View {
 const unsigned char *map;
 uint64_t size;
 unsigned width,height,stride;
 bool rgba;
};

static bool full068_write_all(int fd,const void *data,size_t bytes){
 const auto *p=static_cast<const unsigned char *>(data);
 while(bytes){
  ssize_t n=write(fd,p,bytes);
  if(n<0 && errno==EINTR)continue;
  if(n<=0)return false;
  p+=n;bytes-=size_t(n);
 }
 return true;
}

static bool full068_write_ppm(int dir,const char *name,const Full068View &v,uint64_t *bytes){
 if(!v.map || !v.width || !v.height || v.width>4096 || v.height>4096 ||
    uint64_t(v.stride)<uint64_t(v.width)*4 ||
    uint64_t(v.height-1)*v.stride+uint64_t(v.width)*4>v.size)return false;
 char header[64];int count=snprintf(header,sizeof(header),"P6\n%u %u\n255\n",v.width,v.height);
 if(count<=0 || size_t(count)>=sizeof(header))return false;
 int fd=openat(dir,name,O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);
 if(fd<0)return false;
 bool good=full068_write_all(fd,header,size_t(count));
 unsigned char row[4096*3];
 for(unsigned y=0;good && y<v.height;++y){
  const auto *src=v.map+uint64_t(y)*v.stride;
  for(unsigned x=0;x<v.width;++x){
   row[x*3]=src[x*4+(v.rgba?0:2)];
   row[x*3+1]=src[x*4+1];
   row[x*3+2]=src[x*4+(v.rgba?2:0)];
  }
  good=full068_write_all(fd,row,size_t(v.width)*3);
 }
 if(good && fsync(fd))good=false;
 if(close(fd))good=false;
 if(good)*bytes=uint64_t(count)+uint64_t(v.width)*v.height*3;
 return good;
}

static bool full068_publish_file(int dir,const char *temporary,const char *final){
 if(linkat(dir,temporary,dir,final,0))return false;
 return unlinkat(dir,temporary,0)==0;
}

static bool full068_publish(int dir,uint64_t source_bytes,uint64_t output_bytes,
                           uint64_t mono_us,unsigned fb){
 if(!full068_publish_file(dir,"source.part","source.ppm") ||
    !full068_publish_file(dir,"output.part","output.ppm"))return false;
 int fd=openat(dir,"ready.part",O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);
 if(fd<0)return false;
 char record[256];int size=snprintf(record,sizeof(record),
  "FULL068_READY source_bytes=%llu output_bytes=%llu mono_us=%llu fb=%u\n",
  (unsigned long long)source_bytes,(unsigned long long)output_bytes,
  (unsigned long long)mono_us,fb);
 bool good=size>0 && size_t(size)<sizeof(record) && full068_write_all(fd,record,size_t(size));
 if(good && fsync(fd))good=false;
 if(close(fd))good=false;
 if(good)good=full068_publish_file(dir,"ready.part","ready");
 if(good && fsync(dir))good=false;
 return good;
}
