"""Observe actual samgr profile lookup without changing original activation behavior."""
from pathlib import Path
import runpy,subprocess,re
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-native-original-graphics-boot-013.py'))
inner=p['inner'];capture=p['capture']
tags='SAMGR,CfgPolicy,SAFWK,ParseUtil,AccountMgrService,BMS,Installd,AbilityManagerService,AppSpawn,AMS'
inner,n=re.subn(r'"-T","[^"]+"','"-T","'+tags+'"',inner,count=1);assert n==1
anchor='                graphics_process_005(sample,pid,text);'
assert inner.count(anchor)==1
inner=inner.replace(anchor,r'''
                if(strstr(text,"samgr") && (sample==1 || sample==3)) {
                    const char *suffixes[]={"/environ","/mountinfo","/root/system/profile/installs.json","/root/system/profile","/root/usr/system/profile","/root/system/etc/param/ohos.para"};
                    for(unsigned i=0;i<sizeof(suffixes)/sizeof(suffixes[0]);++i){
                        snprintf(path,sizeof(path),"/proc/%ld%s",pid,suffixes[i]);
                        diagnostic_file_002(sample,path);
                        struct stat st;int rc=stat(path,&st);
                        dprintf(1,"NATIVE_SAMGR014_STAT sample=%u path=%s rc=%d errno=%d mode=%o uid=%u gid=%u\n",sample,path,rc,errno,rc?0:st.st_mode,rc?0:st.st_uid,rc?0:st.st_gid);
                        DIR *dir=opendir(path);if(dir){struct dirent *e;unsigned count=0;while(count++<256 && (e=readdir(dir)))dprintf(1,"NATIVE_SAMGR014_ENTRY path=%s name=%s\n",path,e->d_name);closedir(dir);}
                    }
                    pid_t reader=fork();
                    if(reader==0){alarm(5);execl("/system/bin/param","param","get","const.cust.config_dir_layer",(char*)NULL);_exit(127);}
                }
'''+anchor)
outer=p['outer'].replace('native-original-013-%s','native-original-014-%s')
payload=p['payload'];offset=payload.index('from pathlib import Path\nimport gzip,hashlib')
payload='inner='+repr(inner)+'\nouter='+repr(outer)+'\nWRAPPER='+repr(p['p']['p']['wrapper'])+'\nCAPTURE='+repr(capture)+'\n'+payload[offset:]
payload=payload.replace('native-original-graphics-boot-013','native-original-graphics-boot-014')
if __name__=='__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
