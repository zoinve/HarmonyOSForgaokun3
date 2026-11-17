"""Integrate acknowledged PCM with original audio_host, retaining radio/input306."""
from pathlib import Path
import runpy
import subprocess

BASE=Path(__file__).resolve().parent
INPUT=runpy.run_path(str(BASE/'build-input-native-306.py'))
RADIO=INPUT['RADIO']
ONCE=INPUT['ONCE']
BUILD=Path('/home/zoinve/harmony-virgl-883')

def runtime321(source):
 source=RADIO['runtime297'](source)
 placeholder=r'''    int audio321_node=open("/run/commercial-vendor004/upper/lib64/harmony-graphics/native-audio315.sock",
        O_WRONLY|O_CREAT|O_EXCL|O_CLOEXEC|O_NOFOLLOW,0600);
    if(audio321_node<0||close(audio321_node))fail("audio321 RAM endpoint placeholder");
'''
 source=ONCE(source,'    commercial_vendor016();','    commercial_vendor016();\n'+placeholder)
 binding=r'''    struct stat audio321_node;
    if(lstat("/vendor/lib64/libaudio_primary_impl.z.so",&audio321_node)||!S_ISREG(audio321_node.st_mode)||
       mount("/audio315/libaudio_primary_impl.z.so","/vendor/lib64/libaudio_primary_impl.z.so",NULL,MS_BIND,NULL)||
       mount(NULL,"/vendor/lib64/libaudio_primary_impl.z.so",NULL,MS_BIND|MS_REMOUNT|MS_RDONLY,NULL))
        fail("audio321 original VDI binding");
    if(lstat("/native-audio315.sock",&audio321_node)||!S_ISSOCK(audio321_node.st_mode)||
       audio321_node.st_uid!=3127||(audio321_node.st_mode&0777)!=0600||
       mount("/native-audio315.sock","/vendor/lib64/harmony-graphics/native-audio315.sock",NULL,MS_BIND,NULL))
        fail("audio321 original sandbox endpoint bind");
    dprintf(1,"AUDIO321_VDI original_hdi=1 original_uid=3127 real_pcm_acknowledgements=1 capture_supported=0\n");
'''
 anchor='    dprintf(1,'+chr(34)+'RADIO261_ORIGINAL_HDF'
 return ONCE(source,anchor,binding+anchor)

def outer321(source,old_digest,digest):
 source=INPUT['outer306'](source,old_digest,digest)
 source=source.replace('/commercial61-native-306/bootstrap-runtime087','/commercial61-native-321/bootstrap-runtime087')
 source=ONCE(source,'    pid_t touch306 = -1;','    pid_t touch306 = -1;\n    pid_t audio321 = -1;')
 start=r'''    if(okay){
        audio321=fork();
        if(!audio321){
            setenv("ALSA_CONFIG_DIR","/audio315/share/alsa",1);
            setenv("ALSA_CONFIG_PATH","/audio315/share/alsa/alsa.conf",1);
            setenv("ALSA_CONFIG_UCM2","/audio315/share/alsa/ucm2",1);
            execl("/audio315/lib/ld-linux-aarch64.so.1","audio321-loader","--library-path","/audio315/lib",
                "/audio315/server","/native-target/native-audio315.sock",NULL);
            _exit(90);
        }
        int ready321=0;
        for(unsigned i=0;i<50&&audio321>0;++i){
            struct stat node;
            if(!lstat("/native-target/native-audio315.sock",&node)&&S_ISSOCK(node.st_mode)&&
                node.st_uid==3127&&(node.st_mode&0777)==0600){ready321=1;break;}
            usleep(100000);
        }
        if(!ready321){dprintf(1,"AUDIO321_BROKER unavailable=1 hardware_success_not_inferred=1\n");okay=0;}
    }
'''
 anchor='    if(okay){\n        /* Only the temporary diagnostic kernel:'
 source=ONCE(source,anchor,start+anchor)
 finish=r'''    if(audio321>0){
        kill(audio321,SIGTERM);
        int status321=0;pid_t done321=0;
        for(unsigned i=0;i<40;++i){
            done321=waitpid(audio321,&status321,WNOHANG);
            if(done321==audio321||(done321<0&&errno!=EINTR))break;
            usleep(100000);
        }
        if(!done321){kill(audio321,SIGKILL);while(waitpid(audio321,&status321,0)<0&&errno==EINTR){}}
        dprintf(1,"AUDIO321_BROKER stopped=1 forced=%d raw_wait_status=%d\n",!done321,status321);
    }
'''
 source=ONCE(source,'    int trace285 = open(',finish+'    int trace285 = open(')
 helper=(BASE/'native-bt-observe-294.h').read_text().replace('radio294_observe','audio321_observe')
 helper=helper.replace('3021','3127').replace('blue_host','audio_host').replace('RADIO294_','AUDIO321_')
 helper=helper.replace('libbt_vendor.z.so','libaudio_primary_impl.z.so')
 helper=helper.replace('/radio261/vendor.trace','/vendor/lib64/harmony-graphics/native-audio315.sock')
 helper=helper.replace('/native-bt-broker.sock','/dev/snd/pcmC0D1p')
 source=ONCE(source,'static void native_original(void)\n{',helper+'\nstatic void native_original(void)\n{')
 return ONCE(source,'                if(i==4 && started083)native_live159_start(child);',
     '                if(i==4||i==7)audio321_observe(child);\n                if(i==4 && started083)native_live159_start(child);')

def extra321(compile_program,stage,entries):
 INPUT['extra306'](compile_program,stage,entries)
 headers=BUILD/'audio-contract-314-peripheral/audio/interfaces/sound/v1_0'
 vendor=runpy.run_path(str(BASE/'native-audio-vdi-319.py'))['vendor319']()
 vendor_path=stage/'audio-vdi.c';vendor_path.open('x').write(vendor)
 server_path=stage/'audio-server.c';server_path.open('x').write((BASE/'native-audio-server-316.c').read_text())
 options=['-O2','-Wall','-Wextra','-Werror','-I',str(BASE),'-I',str(headers)]
 compiler=str(BUILD/'window-bridge/toolchain/ohos-cc')
 subprocess.run([compiler,*options,'-shared','-fPIC','-Wl,--no-undefined,-soname,libaudio_primary_impl.z.so',
    str(vendor_path),'-o',str(stage/'libaudio_primary_impl.z.so')],check=True)
 subprocess.run(['aarch64-linux-gnu-gcc',*options,str(server_path),'-ldl','-o',str(stage/'audio-server')],check=True)
 entries['native-target/audio315']=(0o40755,b'')
 entries['native-target/audio315/libaudio_primary_impl.z.so']=(0o100755,(stage/'libaudio_primary_impl.z.so').read_bytes())
 entries['audio315']=(0o40755,b'')
 entries['audio315/server']=(0o100755,(stage/'audio-server').read_bytes())
 assets=BUILD/'audio-assets-314'
 for path in sorted(assets.rglob('*')):
    name='audio315/'+path.relative_to(assets).as_posix()
    assert not path.is_symlink()
    entries[name]=(0o40755,b'') if path.is_dir() else (0o100755 if name.startswith('audio315/lib/') else 0o100644,path.read_bytes())

if __name__=='__main__':
 runpy.run_path(str(BASE/'driver-builder-305.py'))['build'](
    321,runtime321,outer321,RADIO['vendor297'],extra321)
