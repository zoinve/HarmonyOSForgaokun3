"""Export bounded original HarmonyOS crash reports before volatile data disappears."""
from pathlib import Path
import runpy, subprocess, re
base = Path(__file__).resolve().parent
p = runpy.run_path(str(base / 'build-native-original-graphics-boot-017.py'))
inner = p['inner']; capture = p['capture']
helper = r'''
static void native_fault_walk_018(int dir,const char *path,unsigned depth,unsigned sample,
                                  unsigned *files,unsigned *total)
{
    DIR *stream=fdopendir(dup(dir));if(!stream)return;
    struct dirent *entry;
    while(*files<64 && *total<8388608 && (entry=readdir(stream))){
        if(!strcmp(entry->d_name,".") || !strcmp(entry->d_name,".."))continue;
        struct stat st;
        if(fstatat(dir,entry->d_name,&st,AT_SYMLINK_NOFOLLOW))continue;
        char name[1024];int len=snprintf(name,sizeof(name),"%s/%s",path,entry->d_name);
        if(len<0 || (size_t)len>=sizeof(name))continue;
        if(S_ISDIR(st.st_mode) && depth<4){
            int child=openat(dir,entry->d_name,O_RDONLY|O_DIRECTORY|O_CLOEXEC|O_NOFOLLOW);
            if(child>=0){native_fault_walk_018(child,name,depth+1,sample,files,total);close(child);}
        }else if(S_ISREG(st.st_mode)){
            ++*files;
            int fd=openat(dir,entry->d_name,O_RDONLY|O_CLOEXEC|O_NOFOLLOW);
            dprintf(1,"NATIVE_FAULT018_BEGIN sample=%u path=%s size=%lld fd=%d errno=%d\n",sample,name,(long long)st.st_size,fd,fd<0?errno:0);
            if(fd<0)continue;
            unsigned offset=0;unsigned char data[128];ssize_t n=0;
            while(offset<2097152 && *total<8388608 && (n=read(fd,data,sizeof(data)))>0){
                char hex[257];for(ssize_t j=0;j<n;++j)snprintf(hex+j*2,3,"%02x",data[j]);
                dprintf(1,"NATIVE_FAULT018_HEX sample=%u path=%s offset=%u data=%s\n",sample,name,offset,hex);
                offset+=(unsigned)n;*total+=(unsigned)n;
            }
            struct stat end;int changed=fstat(fd,&end) || end.st_size!=st.st_size || end.st_mtime!=st.st_mtime;
            close(fd);
            dprintf(1,"NATIVE_FAULT018_END sample=%u path=%s bytes=%u complete=%d changed=%d read_errno=%d\n",sample,name,offset,(long long)offset==st.st_size,changed,n<0?errno:0);
        }
    }
    closedir(stream);
}
static void native_fault_capture_018(unsigned sample)
{
    const char *paths[]={"/data/log/faultlog","/data/log/hiview/stack"};
    unsigned files=0,total=0;
    for(unsigned i=0;i<sizeof(paths)/sizeof(paths[0]);++i){
        int fd=open(paths[i],O_RDONLY|O_DIRECTORY|O_CLOEXEC|O_NOFOLLOW);
        dprintf(1,"NATIVE_FAULT018_DIRECTORY sample=%u path=%s fd=%d errno=%d\n",sample,paths[i],fd,fd<0?errno:0);
        if(fd>=0){native_fault_walk_018(fd,paths[i],0,sample,&files,&total);close(fd);}
    }
    dprintf(1,"NATIVE_FAULT018_CAPTURE sample=%u files=%u bytes=%u bounded=1\n",sample,files,total);
}
'''
anchor = 'static void graphics_observer_047(void)'
assert inner.count(anchor) == 1
inner = inner.replace(anchor, helper + '\n' + anchor)
anchor = '        diagnostic_state_002(sample);'
assert inner.count(anchor) == 1
inner = inner.replace(anchor, '        if(sample==2 || sample==5 || sample==8 || sample==11)native_fault_capture_018(sample);\n' + anchor)
tags = 'FaultLogger,DfxSignalHandler,DfxException,DfxProcessDump,AppFreeze,AMS,BluetoothHost,BluetoothService,BT_SERVICE,HiView-Engine'
inner, n = re.subn(r'"-T","[^"]+"', '"-T","' + tags + '"', inner, count=1)
assert n == 1
outer = p['outer'].replace('native-original-017-%s','native-original-018-%s')
payload = p['payload']; offset = payload.index('from pathlib import Path\nimport gzip,hashlib')
# Reuse the exact storage wrapper and all prior build/identity/hash guards.
prefix = payload[:offset]
wrapper = prefix[prefix.index('WRAPPER=')+len('WRAPPER='):prefix.index('\nCAPTURE=')]
payload = 'inner='+repr(inner)+'\nouter='+repr(outer)+'\nWRAPPER='+wrapper+'\nCAPTURE='+repr(capture)+'\n'+payload[offset:]
payload = payload.replace('native-original-graphics-boot-017','native-original-graphics-boot-018')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
