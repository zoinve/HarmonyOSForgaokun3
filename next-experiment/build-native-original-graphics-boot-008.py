"""Retry real original hilog startup; no service or graphics return-value changes."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent;p=runpy.run_path(str(base/'build-native-original-graphics-boot-007.py'))
inner=p['inner']
old='''        sleep(3);alarm(60);
        execl("/system/bin/hilog","hilog","-T","COMPOSER_SRV,RSScreenManager,RSHardwareThread,HdiBackend,HdiDevice,RSMainThread",(char*)NULL);
        _exit(127);'''
new='''        alarm(65);
        for(int ready=0;ready<15 && access("/dev/unix/socket/hilogOutput",F_OK);ready++)sleep(1);
        pid_t config=fork();
        if(config==0){execl("/system/bin/hilog","hilog","-b","D",(char*)NULL);_exit(127);}
        if(config>0)waitpid(config,NULL,0);
        for(int attempt=0;attempt<8;attempt++){
            pid_t reader=fork();
            if(reader==0){execl("/system/bin/hilog","hilog","-T","COMPOSER_SRV,RSScreenManager,RSHardwareThread,HdiBackend,HdiDevice,RSMainThread",(char*)NULL);_exit(127);}
            int status=-1;if(reader>0)waitpid(reader,&status,0);
            dprintf(1,"NATIVE_HILOG008_RETRY attempt=%d status=%d\\n",attempt,status);sleep(1);
        }
        _exit(0);'''
assert inner.count(old)==1
inner=inner.replace(old,new)
outer=p['outer'].replace('native-original-007-%s','native-original-008-%s')
payload=p['payload'];offset=payload.index('from pathlib import Path\nimport gzip,hashlib')
payload='inner='+repr(inner)+'\nouter='+repr(outer)+'\n'+payload[offset:]
payload=payload.replace('native-original-graphics-boot-007','native-original-graphics-boot-008')
if __name__=='__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
