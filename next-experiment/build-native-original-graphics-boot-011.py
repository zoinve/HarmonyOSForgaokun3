"""Target-only, service-local single-device HMDFS views; no distributed emulation."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-native-original-graphics-boot-010.py'))
wrapper=r'''#include <stdlib.h>
#include <unistd.h>
int main(void){
 if(geteuid()!=0)return 77;
 if(setenv("LD_PRELOAD","/system/lib64/libnative_local_storage_001.so",1))return 78;
 char *args[]={"/system/bin/storage_daemon",NULL};
 execv("/system/bin/storage_daemon",args);return 79;
}
'''
inner=p['inner'];outer=p['outer'].replace('native-original-010-%s','native-original-011-%s')
anchor='    graphics_egl_054();'
assert inner.count(anchor)==1
inner=inner.replace(anchor,anchor+r'''
    const char *local_from[]={"/storage_daemon-local.cfg","/native-storage-local","/libnative_local_storage_001.so"};
    const char *local_to[]={"/system/etc/init/storage_daemon.cfg","/system/bin/native-storage-local","/system/lib64/libnative_local_storage_001.so"};
    for(unsigned i=0;i<3;++i){
        if(i){int f=open(local_to[i],O_WRONLY|O_CREAT|O_EXCL|O_CLOEXEC,i==1?0755:0644);if(f<0||close(f))fail("local storage bind target");}
        if(mount(local_from[i],local_to[i],NULL,MS_BIND,NULL) ||
           mount(NULL,local_to[i],NULL,MS_BIND|MS_REMOUNT|MS_RDONLY,NULL))fail("service-local storage bind");
    }
    dprintf(1,"NATIVE_STORAGE011 local_bind_views=1 distributed_support=0 service_only=storage_daemon\n");
''')
extra=r'''
ref=project/'references/L410-HarmonyOS-Adaptations/storage-hmdfs/storage_hmdfs_compat_shim.c'
ref_sha=sha(ref)
shim=work/'libnative_local_storage_001.so'
tool=root/'window-bridge/toolchain'
command=[str(tool/'ohos-cc'),'-shared','-fPIC','-O2','-Wall','-Wextra','-Werror',str(ref),'-Wl,--no-undefined,-soname,libnative_local_storage_001.so','-o',str(shim)]
r=subprocess.run(command,capture_output=True,text=True)
(local/'storage-compile.stdout').write_text(r.stdout);(local/'storage-compile.stderr').write_text(r.stderr)
assert r.returncode==0,r.stderr
assert sha(ref)==ref_sha
src=work/'storage-wrapper.c';src.write_text(WRAPPER)
subprocess.run(['aarch64-linux-gnu-gcc','-static','-O2','-Wall','-Wextra','-Werror',str(src),'-o',str(work/'native-storage-local')],check=True)
original=subprocess.run(['debugfs','-R','cat /system/etc/init/storage_daemon.cfg','/mnt/d/Download/pc_all_arm/system.img'],capture_output=True,text=True,check=True).stdout
config=json.loads(original);before=json.loads(original)
assert len(config['services'])==1 and config['services'][0]['name']=='storage_daemon'
assert config['services'][0]['path']==['/system/bin/storage_daemon']
config['services'][0]['path']=['/system/bin/native-storage-local']
restored=json.loads(json.dumps(config));restored['services'][0]['path']=before['services'][0]['path']
assert restored==before
cfg=work/'storage_daemon-local.cfg';cfg.write_text(json.dumps(config,indent=2)+'\n')
file('native-target/storage_daemon-local.cfg',cfg)
file('native-target/native-storage-local',work/'native-storage-local',0o755)
file('native-target/libnative_local_storage_001.so',shim)
with (local/'storage-compatibility.json').open('x') as f:
 json.dump(dict(reference_sha256=ref_sha,library_sha256=sha(shim),wrapper_sha256=sha(work/'native-storage-local'),original_config=before,local_config=config,scope='local single-device bind views only; real non-HMDFS errors retained; storage_daemon only',command=command),f,indent=2)
'''
payload=p['payload'];offset=payload.index('from pathlib import Path\nimport gzip,hashlib')
payload='inner='+repr(inner)+'\nouter='+repr(outer)+'\nWRAPPER='+repr(wrapper)+'\n'+payload[offset:]
payload=payload.replace('native-original-graphics-boot-010','native-original-graphics-boot-011')
anchor="file('init',work/'init',0o755)"
assert payload.count(anchor)==1
payload=payload.replace(anchor,extra+'\n'+anchor)
if __name__=='__main__':
 raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
