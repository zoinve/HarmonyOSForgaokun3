"""Test original SDK BinderConnector methods with a read-only extracted DSO closure."""
from pathlib import Path
import runpy
import subprocess

base=Path(__file__).resolve().parent
parent=runpy.run_path(str(base/'prepare-baremetal-identity-sdk-007.py'))
source=parent['source'];anchor='    pid_t sdk_child=fork();'
assert source.count(anchor)==1
source=source.replace(anchor,'''    require(symlink("/dev/binderfs/identity002","/dev/binder")==0,"private QEMU Binder path for original SDK connector");
    pid_t sdk_child=fork();''').replace('IDENTITY007_','IDENTITY008_')
sdk_source=parent['sdk_source'].replace('SDK007_','SDK008_')
anchor='    printf("SDK008_PASS checks='
assert sdk_source.count(anchor)==1
connector=r'''    void *ipc=dlopen("libipc_common.z.so",RTLD_NOW|RTLD_LOCAL);
    if(!ipc)fprintf(stderr,"IPC008_DLOPEN %s\n",dlerror());
    check(ipc!=NULL,"load unmodified SDK IPC common and dependencies");
    void *(*instance)(void)=dlsym(ipc,"_ZN4OHOS15BinderConnector11GetInstanceEv");
    _Bool (*alive)(void *)=dlsym(ipc,"_ZN4OHOS15BinderConnector13IsDriverAliveEv");
    _Bool (*access)(void *)=dlsym(ipc,"_ZN4OHOS15BinderConnector22IsAccessTokenSupportedEv");
    _Bool (*realpid)(void *)=dlsym(ipc,"_ZN4OHOS15BinderConnector18IsRealPidSupportedEv");
    _Bool (*refresh)(void *)=dlsym(ipc,"_ZN4OHOS15BinderConnector18IsRefreshSupportedEv");
    _Bool (*userinfo)(void *)=dlsym(ipc,"_ZN4OHOS15BinderConnector26IsCallingUserInfoSupportedEv");
    uint64_t (*own)(void *)=dlsym(ipc,"_ZN4OHOS15BinderConnector14GetSelfTokenIDEv");
    uint64_t (*own_first)(void *)=dlsym(ipc,"_ZN4OHOS15BinderConnector25GetSelfFirstCallerTokenIDEv");
    check(instance&&alive&&access&&realpid&&refresh&&userinfo&&own&&own_first,"resolve original connector methods");
    void *connection=instance();
    check(connection!=NULL&&alive(connection),"original connector accepts protocol 8 and maps real Binder device");
    check(access(connection)&&realpid(connection),"original connector observes token and real-PID feature bits");
    check(!refresh(connection)&&!userinfo(connection),"original connector does not advertise unsupported features");
    check(own(connection)==self&&own_first(connection)==first,"original connector reads current authentic task identity");
    printf("IPC008_PASS protocol_accepted=1 access_token=1 real_pid=1 unsupported_features=0 task_tokens_preserved=1 transactions_not_tested=1\n");
'''
sdk_source=sdk_source.replace(anchor,connector+anchor)
payload=parent['payload'];payload=payload[payload.index('from pathlib import Path'):]
payload='source='+repr(source)+'\nsdk_source='+repr(sdk_source)+'\n'+payload
payload=payload.replace('baremetal-identity-sdk-007','baremetal-identity-connector-008')
anchor="(work/'init.c').write_text(source);(work/'sdk-probe.c').write_text(sdk_source)"
assert payload.count(anchor)==1
closure=r'''
import posixpath
closure_paths={}
def extract_library(name):
 assert re.fullmatch(r'[A-Za-z0-9_.+-]+',name),name
 dest=sdk/name
 if dest.exists():return
 selected=None
 for directory in ['/system/lib64/platformsdk','/system/lib64/chipset-sdk-sp','/system/lib64','/system/lib64/ndk']:
  path=directory+'/'+name
  r=subprocess.run(['debugfs','-R','stat '+path,system],capture_output=True,text=True,timeout=15)
  if 'Inode:' in r.stdout:selected=path;break
 assert selected,name
 for _ in range(8):
  r=subprocess.run(['debugfs','-R','stat '+selected,system],capture_output=True,text=True,timeout=15)
  assert 'Inode:' in r.stdout,(selected,r.stderr)
  if 'Type: symlink' not in r.stdout:break
  m=re.search(r'Fast link dest: "([^\n"]+)"',r.stdout);assert m,(selected,r.stdout)
  selected=posixpath.normpath(posixpath.join(posixpath.dirname(selected),m[1]))
  assert selected.startswith('/system/lib64/'),selected
 else:raise AssertionError('symlink chain too deep')
 run(['debugfs','-R','dump '+selected+' '+str(dest),system],'extract-'+name)
 assert dest.is_file() and dest.stat().st_size>0,name
 closure_paths[name]=selected
pending=['libipc_common.z.so'];visited=set()
while pending:
 name=pending.pop()
 if name in visited or name=='libc.so':continue
 assert len(visited)<64
 extract_library(name);visited.add(name)
 d=run(['aarch64-linux-gnu-readelf','-d',str(sdk/name)],'closure-'+name)
 pending.extend(re.findall(r'Shared library: \[([^]]+)\]',d))
assert sum(p.stat().st_size for p in sdk.iterdir())<64*1024*1024
'''
payload=payload.replace(anchor,closure+'\n'+anchor)
payload=payload.replace("for name in ['loader','probe','libtokensetproc_shared.z.so','libsec_shared.z.so']:","for name in sorted(p.name for p in sdk.iterdir() if p.is_file()):")
payload=payload.replace("assert all(n in ['libc.so','libsec_shared.z.so'] for n in needed),(name,needed)","assert all(n=='libc.so' or (sdk/n).is_file() for n in needed),(name,needed)")
payload=payload.replace('runtime_verified=False,images_modified=False','runtime_verified=False,connector_runtime_verified=False,original_closure_paths=closure_paths,images_modified=False')
compile(payload,'prepare-connector-008','exec')
if __name__=='__main__':
    result=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=300)
    raise SystemExit(result.returncode)
