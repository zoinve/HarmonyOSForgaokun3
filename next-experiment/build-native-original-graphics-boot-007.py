"""Early original-screen logs and independent constructor/kernel trace channels."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-native-original-graphics-boot-006.py'))
inner=p['inner'].replace('native-composer-006','native-composer-007')
anchor='    pid_t observer = fork();'
inner=inner.replace(anchor,'''    if(fork()==0){
        sleep(3);alarm(60);
        execl("/system/bin/hilog","hilog","-T","COMPOSER_SRV,RSScreenManager,RSHardwareThread,HdiBackend,HdiDevice,RSMainThread",(char*)NULL);
        _exit(127);
    }
'''+anchor)
outer=p['outer'].replace('native-original-006-%s','native-original-007-%s')
payload=p['payload'];offset=payload.index('from pathlib import Path\nimport gzip,hashlib')
payload='inner='+repr(inner)+'\nouter='+repr(outer)+'\n'+payload[offset:]
payload=payload.replace('native-original-graphics-boot-006','native-original-graphics-boot-007').replace('native-composer-006','native-composer-007').replace('NATIVE_COMPOSER006','NATIVE_COMPOSER007').replace('native_trace_006','native_trace_007')
anchor='        int fd=open("/data/native-composer-007.trace"'
assert payload.count(anchor)==1
payload=payload.replace(anchor,'''        int kernel=open("/dev/kmsg",O_WRONLY|O_CLOEXEC);
        if(kernel>=0){dprintf(kernel,"NATIVE_COMPOSER007 pid=%d uid=%d call=%s value=%d errno=%d\\n",getpid(),getuid(),name,value,saved);close(kernel);}
'''+anchor)
anchor='source=original.replace('
payload=payload.replace(anchor,'''helper+='\\n__attribute__((constructor)) static void native_constructor_007(){native_trace_007("library_constructor",0); }\\n'
'''+anchor)
if __name__=='__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
