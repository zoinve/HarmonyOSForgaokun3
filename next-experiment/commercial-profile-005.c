#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <fcntl.h>
#include <dirent.h>
#include <dlfcn.h>
#include <errno.h>
#include <string.h>
#include <sys/stat.h>

/* Observe the real commercial config-policy library under init-assigned samgr credentials. */
static void directory(FILE *out,const char *path)
{
    DIR *d=opendir(path);fprintf(out,"DIRECTORY %s open=%d errno=%d\n",path,d!=NULL,errno);
    if(!d)return;
    struct dirent *e;unsigned count=0,json=0;
    while((e=readdir(d))){
        ++count;size_t n=strlen(e->d_name);
        if(n>5 && !strcmp(e->d_name+n-5,".json"))++json;
        if(count<9 || !strcmp(e->d_name,"installs.json"))fprintf(out,"ENTRY %s type=%u\n",e->d_name,e->d_type);
    }
    fprintf(out,"DIRECTORY_TOTAL entries=%u json=%u\n",count,json);closedir(d);
}
static void inspect(FILE *out)
{
    fprintf(out,"COMMERCIAL005_PROFILE pid=%d uid=%d euid=%d gid=%d\n",getpid(),getuid(),geteuid(),getgid());
    void *h=dlopen("/system/lib64/chipset-sdk-sp/libconfigpolicy_util.z.so",RTLD_NOW|RTLD_LOCAL);
    if(!h){fprintf(out,"DLOPEN %s\n",dlerror());return;}
    void *(*getdirs)(void)=(void *(*)(void))dlsym(h,"GetCfgDirList");
    void *(*getfiles)(const char *)=(void *(*)(const char *))dlsym(h,"GetCfgFiles");
    void (*freedirs)(void *)=(void (*)(void *))dlsym(h,"FreeCfgDirList");
    void (*freefiles)(void *)=(void (*)(void *))dlsym(h,"FreeCfgFiles");
    int (*readparam)(const char *,char *,unsigned *)=(int (*)(const char *,char *,unsigned *))dlsym(h,"SystemReadParam");
    char value[4097]={0};unsigned length=4096;
    if(readparam){int r=readparam("const.cust.config_dir_layer",value,&length);value[4096]=0;fprintf(out,"PARAM result=%d length=%u value=%s\n",r,length,value);}
    if(getdirs && freedirs){
        void *p=getdirs();if(p){char **paths=p;for(unsigned i=0;i<32;++i)if(paths[i])fprintf(out,"CFG_DIR %u %s\n",i,paths[i]);freedirs(p);}
    }
    if(getfiles && freefiles){
        void *p=getfiles("profile");fprintf(out,"CFG_FILES result=%d\n",p!=NULL);
        if(p){char **paths=p;for(unsigned i=0;i<32;++i)if(paths[i]){fprintf(out,"CFG_PATH %u %s\n",i,paths[i]);directory(out,paths[i]);}freefiles(p);}
    }
    directory(out,"/system/profile");
    FILE *f=fopen("/system/profile/installs.json","re");
    fprintf(out,"INSTALLS_PROFILE open=%d errno=%d\n",f!=NULL,errno);
    if(f){char b[2048];size_t n=fread(b,1,sizeof(b),f);fwrite(b,1,n,out);fclose(f);}
    dlclose(h);
}
int main(int argc,char **argv)
{
    (void)argc;
    int fd=open("/run/commercial-profile005/profile.log",O_WRONLY|O_CREAT|O_EXCL|O_CLOEXEC|O_NOFOLLOW,0640);
    if(fd>=0){FILE *out=fdopen(fd,"w");if(out){inspect(out);fclose(out);}else close(fd);}
    argv[0]="/system/bin/samgr";
    execv("/system/bin/samgr",argv);
    dprintf(2,"COMMERCIAL005 original samgr exec failed errno=%d\n",errno);return 111;
}
