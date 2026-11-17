"""Compile platform adapter and test narrow interposition plus state handling."""
from pathlib import Path
import json
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'next-experiment'
BUILD=Path('/home/zoinve/harmony-virgl-883')
FIXTURE=r'''
#include <stdio.h>
#include <fcntl.h>
int fixture_open376(const char *path,int flags){return open(path,flags);}
FILE *fixture_fopen376(const char *path,const char *mode){return fopen(path,mode);}
'''
CLIENT=r'''
#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
int fixture_open376(const char *,int);
FILE *fixture_fopen376(const char *,const char *);
int main(void){
 assert(fixture_open376("/dev/input/event1",O_RDONLY)<0&&errno==ENODEV);
 assert(fixture_open376("/dev/input/event2",O_RDONLY)<0&&errno==ENOENT);
 assert(fixture_open376("/dev/input/event3",O_RDONLY)<0&&errno==ENOENT);
 assert(fixture_open376("/dev/input/event4",O_RDONLY)<0&&errno==ENOENT);
 assert(!fixture_fopen376("/sys/class/switch/h2w/state","r")&&errno==ENODEV);
 int fd=open("passthrough",O_WRONLY|O_CREAT|O_EXCL,0640);assert(fd>=0);
 assert(write(fd,"ok",2)==2);close(fd);
 FILE *f=fixture_fopen376("passthrough","r");assert(f);
 char b[3]={0};assert(fread(b,1,2,f)==2&&!strcmp(b,"ok"));fclose(f);
 struct stat s;assert(!stat("passthrough",&s)&&(s.st_mode&0777)==0640);
 puts("AUDIO377_INTERPOSITION passed=1 exact_policy_caller_only=1 passthrough_files_unchanged=1 missing_jack_is_error=1 hardware_acceptance=0");
 return 0;
}
'''
if __name__=='__main__':
    report=ROOT/'reports/audio-jack-test-377.json';assert not report.exists()
    with tempfile.TemporaryDirectory(prefix='audio377-') as temporary:
        stage=Path(temporary)
        compiler=str(BUILD/'window-bridge/toolchain/ohos-cc')
        flags=['-O2','-Wall','-Wextra','-Werror']
        source=BASE/'native-audio-jack-376.c'
        subprocess.run([compiler,*flags,'-fvisibility=hidden','-shared','-fPIC',
            '-Wl,--no-undefined',str(source),'-ldl','-pthread','-o',str(stage/'platform.so')],check=True)
        subprocess.run(['gcc',*flags,'-fvisibility=hidden','-shared','-fPIC',str(source),
            '-ldl','-pthread','-o',str(stage/'adapter.so')],check=True)
        subprocess.run(['gcc','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
            '-I',str(BASE),str(BASE/'test-audio-jack-377.c'),'-ldl','-pthread','-o',str(stage/'unit')],check=True)
        unit=subprocess.run([str(stage/'unit')],capture_output=True,text=True,check=True,timeout=20)
        (stage/'fixture.c').open('x').write(FIXTURE)
        (stage/'client.c').open('x').write(CLIENT)
        subprocess.run(['gcc',*flags,'-fno-optimize-sibling-calls','-shared','-fPIC',
            str(stage/'fixture.c'),'-o',str(stage/'libaudio_policy_service.z.so')],check=True)
        subprocess.run(['gcc',*flags,str(stage/'client.c'),'-L',str(stage),
            '-l:libaudio_policy_service.z.so','-Wl,-rpath,'+str(stage),'-o',str(stage/'client')],check=True)
        import os
        environment=dict(os.environ,LD_PRELOAD=str(stage/'adapter.so'))
        integration=subprocess.run([str(stage/'client')],cwd=stage,env=environment,
            capture_output=True,text=True,check=True,timeout=20)
        symbols=subprocess.check_output(['readelf','--dyn-syms','--wide',str(stage/'platform.so')],text=True)
        defined=[]
        for line in symbols.splitlines():
            parts=line.split()
            if len(parts)>=8 and parts[3]=='FUNC' and parts[4]=='GLOBAL' and parts[6]!='UND':
                defined.append(parts[7])
        assert set(defined)-{'_init','_fini'}=={'fopen','open'},defined
        defined=[name for name in defined if name not in {'_init','_fini'}]
    result=dict(platform_adapter_built=True,exported_symbols=sorted(defined),
        sanitizers_passed=True,unit_stdout=unit.stdout,interposition_stdout=integration.stdout,
        hardware_acceptance=False,credentials_changed=False,input_injected=False,microphone_recorded=False)
    report.open('x').write(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
