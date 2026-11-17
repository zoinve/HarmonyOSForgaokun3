"""Observe only known original UI filesystem paths; no private memory reads."""
HELPER = r'''
static void resource069_path(unsigned sample,long pid,const char *root,const char *relative){
 const int saved069=errno;
 char path069[1024];int length069=snprintf(path069,sizeof(path069),"%s%s",root,relative);
 if(length069<=0 || (size_t)length069>=sizeof(path069)){errno=saved069;return;}
 struct stat link069={0},target069={0};
 int lr069=lstat(path069,&link069),le069=lr069?errno:0;
 int sr069=stat(path069,&target069),se069=sr069?errno:0;
 char canonical069[4096];char *resolved069=realpath(path069,canonical069);
 int re069=resolved069?0:errno;
 dprintf(commercial_diag_fd003,"COMMERCIAL069_RESOURCE_STAT sample=%u pid=%ld path=%s lstat=%d lerrno=%d stat=%d serrno=%d uid=%u gid=%u mode=%o size=%lld dev=%llu inode=%llu real_errno=%d real=%s root_observation_not_app_access_proof=1\n",
  sample,pid,relative,lr069,le069,sr069,se069,sr069?0:(unsigned)target069.st_uid,
  sr069?0:(unsigned)target069.st_gid,sr069?0:(unsigned)target069.st_mode,
  sr069?0:(long long)target069.st_size,sr069?0:(unsigned long long)target069.st_dev,
  sr069?0:(unsigned long long)target069.st_ino,re069,resolved069?canonical069:"unresolved");
 if(!sr069 && S_ISDIR(target069.st_mode)){
  DIR *dir069=opendir(path069);struct dirent *entry069;unsigned count069=0;
  if(dir069){
   while(count069<32 && (entry069=readdir(dir069))){
    if(!strcmp(entry069->d_name,".") || !strcmp(entry069->d_name,".."))continue;
    ++count069;
    dprintf(commercial_diag_fd003,"COMMERCIAL069_RESOURCE_ENTRY sample=%u pid=%ld path=%s name=%s type=%u\n",
      sample,pid,relative,entry069->d_name,(unsigned)entry069->d_type);
   }
   closedir(dir069);
  }
 }else if(!sr069 && S_ISREG(target069.st_mode)){
  int fd069=open(path069,O_RDONLY|O_NOFOLLOW|O_CLOEXEC);
  unsigned char prefix069[64];ssize_t count069=fd069>=0?read(fd069,prefix069,sizeof(prefix069)):-1;
  int error069=count069<0?errno:0;
  if(fd069>=0)close(fd069);
  char hex069[129]={0};const char digits069[]="0123456789abcdef";
  for(ssize_t i069=0;i069<count069;++i069){hex069[i069*2]=digits069[prefix069[i069]>>4];hex069[i069*2+1]=digits069[prefix069[i069]&15];}
  dprintf(commercial_diag_fd003,"COMMERCIAL069_RESOURCE_PREFIX sample=%u pid=%ld path=%s bytes=%zd errno=%d hex=%s\n",
    sample,pid,relative,count069,error069,hex069);
 }
 errno=saved069;
}

static void commercial_resource_inventory069(unsigned sample,long pid){
 if(sample<8 || sample>29 || sample%2)return;
 const int saved069=errno;
 char root069[64];snprintf(root069,sizeof(root069),"/proc/%ld/root",pid);
 const char *paths069[]={
  "/system/app/HwStartupGuide", "/system/app/HwStartupGuide/HwStartupGuide.hap",
  "/system/app/HwStartupGuide/resources", "/system/app/HwStartupGuide/resources/rawfile/welcome_land_one.mp4",
  "/system/app/SystemResources", "/system/app/SystemResources/SystemResources.hap",
  "/data/app/el1/bundle/public/com.huawei.hmos.hwstartupguide",
  "/data/app/el1/bundle/public/com.huawei.hmos.hwstartupguide/pc_hwstartupguide",
  "/data/app/el1/bundle/public/com.huawei.hmos.hwstartupguide/pc_hwstartupguide/resources.index",
  "/data/app/el1/bundle/public/com.huawei.hmos.hwstartupguide/pc_hwstartupguide/resources/rawfile/welcome_land_one.mp4",
  "/data/storage/el1/bundle", "/data/storage/el1/bundle/pc_hwstartupguide",
  "/data/storage/el1/bundle/pc_hwstartupguide/resources.index",
  "/data/storage/el1/bundle/pc_hwstartupguide/resources/rawfile/welcome_land_one.mp4",
  "/data/storage/el1/bundle/pc_hwstartupguide/resources/rawfile/welcome_land_two.mp4"
 };
 for(unsigned i069=0;i069<sizeof(paths069)/sizeof(paths069[0]);++i069)
  resource069_path(sample,pid,root069,paths069[i069]);
 if(sample==10 || sample==18){
  char mounts069[64];snprintf(mounts069,sizeof(mounts069),"/proc/%ld/mountinfo",pid);
  commercial_stream043(mounts069,sample,(unsigned)pid,65536);
 }
 errno=saved069;
}
'''


def instrument(source):
    anchor = 'static void commercial_observer(void)'
    assert source.count(anchor) == 1 and 'COMMERCIAL069_RESOURCE_STAT' not in source
    source = source.replace(anchor, HELPER + '\n' + anchor, 1)
    anchor = "            for(ssize_t i=0;i<n;++i)if(!text[i])text[i]=' ';"
    assert source.count(anchor) == 1
    return source.replace(anchor,
        '            if(!strcmp(text,"com.huawei.hmos.hwstartupguide"))commercial_resource_inventory069(sample,id);\n'
        + anchor, 1)
