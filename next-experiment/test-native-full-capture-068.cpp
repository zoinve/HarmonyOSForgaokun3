#include "native-full-capture-068.h"
#include "native-full-export-068.h"
#include <cassert>
#include <cstring>
#include <string>
#include <sys/wait.h>

static int directory(const std::string &name){
 assert(mkdir(name.c_str(),0700)==0);
 int fd=open(name.c_str(),O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);
 assert(fd>=0);return fd;
}
static void record(int dir,const char *name,const char *data){
 int fd=openat(dir,name,O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);
 assert(fd>=0 && full068_write_all(fd,data,strlen(data)) && close(fd)==0);
}
static void worker(int source,int dest,uid_t owner,int expected){
 pid_t child=fork();assert(child>=0);
 if(!child){full068_export_context context={source,dest,owner};full068_export_worker(&context);_exit(0);}
 int status=0;assert(waitpid(child,&status,0)==child);
 assert(WIFEXITED(status) && WEXITSTATUS(status)==expected);
}
int main(int argc,char **argv){
 assert(argc==2);std::string root=argv[1];
 int input=directory(root+"/input"),output=directory(root+"/output");
 unsigned char rgba[32]={},bgra[32]={};
 for(unsigned y=0;y<2;++y)for(unsigned x=0;x<3;++x){
  unsigned i=y*16+x*4;
  rgba[i]=10+y*20+x;rgba[i+1]=30+x;rgba[i+2]=80+y;rgba[i+3]=255;
  bgra[i]=rgba[i+2];bgra[i+1]=rgba[i+1];bgra[i+2]=rgba[i];bgra[i+3]=17;
 }
 unsigned char saved_rgba[32],saved_bgra[32];
 memcpy(saved_rgba,rgba,32);memcpy(saved_bgra,bgra,32);
 Full068View source={rgba,sizeof(rgba),3,2,16,true};
 Full068View target={bgra,sizeof(bgra),3,2,16,false};
 uint64_t source_bytes=0,output_bytes=0;
 Full068View invalid=source;invalid.size=27;
 assert(!full068_write_ppm(input,"invalid.part",invalid,&source_bytes));
 assert(faccessat(input,"invalid.part",F_OK,AT_SYMLINK_NOFOLLOW)!=0);
 invalid=source;invalid.width=4097;assert(!full068_write_ppm(input,"invalid.part",invalid,&source_bytes));
 invalid=source;invalid.stride=11;assert(!full068_write_ppm(input,"invalid.part",invalid,&source_bytes));
 invalid=source;invalid.height=0;assert(!full068_write_ppm(input,"invalid.part",invalid,&source_bytes));
 assert(symlinkat("../not-created",input,"symlink.part")==0);
 assert(!full068_write_ppm(input,"symlink.part",source,&source_bytes));
 assert(full068_write_ppm(input,"source.part",source,&source_bytes));
 assert(full068_write_ppm(input,"output.part",target,&output_bytes));
 assert(!full068_write_ppm(input,"source.part",source,&source_bytes));
 assert(faccessat(input,"ready",F_OK,AT_SYMLINK_NOFOLLOW)!=0);
 assert(full068_publish(input,source_bytes,output_bytes,120123456,77));
 assert(!full068_publish(input,source_bytes,output_bytes,120123456,77));
 assert(memcmp(saved_rgba,rgba,32)==0 && memcmp(saved_bgra,bgra,32)==0);
 worker(input,output,geteuid(),0);
 worker(input,output,geteuid(),126);
 int bad_owner=directory(root+"/reject-owner");
 worker(input,bad_owner,geteuid()+1,126);close(bad_owner);
 int invalid_marker=directory(root+"/invalid-marker"),bad_marker=directory(root+"/reject-marker");
 record(invalid_marker,"ready","FULL068_READY source_bytes=1\n");
 worker(invalid_marker,bad_marker,geteuid(),126);close(invalid_marker);close(bad_marker);
 int symlink_source=directory(root+"/symlink-source"),bad_symlink=directory(root+"/reject-symlink");
 char marker[256];snprintf(marker,sizeof(marker),"FULL068_READY source_bytes=%llu output_bytes=%llu mono_us=120123456 fb=77\n",
  (unsigned long long)source_bytes,(unsigned long long)output_bytes);
 record(symlink_source,"ready",marker);
 assert(symlinkat("../input/source.ppm",symlink_source,"source.ppm")==0);
 worker(symlink_source,bad_symlink,geteuid(),126);close(symlink_source);close(bad_symlink);
 int huge=directory(root+"/huge-source"),bad_size=directory(root+"/reject-size");
 record(huge,"ready","FULL068_READY source_bytes=999999999 output_bytes=1 mono_us=120123456 fb=77\n");
 worker(huge,bad_size,geteuid(),126);close(huge);close(bad_size);
 close(input);close(output);
}
