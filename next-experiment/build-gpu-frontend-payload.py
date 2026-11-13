"""Fresh 885: diagnose real product EGL loading, preserving 883 library overlay."""
from pathlib import Path
import subprocess

base = Path(__file__).resolve().parent
out = base / 'payload-885'
assert not out.exists()
source = (base / 'payload-883/init.c').read_text()
anchor = '    ui_snapshot();'
assert source.count(anchor) == 1
probe = r'''
    DIR *gpu_proc=opendir("/proc");struct dirent *gpu_entry;
    if(gpu_proc) {
      while((gpu_entry=readdir(gpu_proc))) {
        if(!atoi(gpu_entry->d_name))continue;
        char path[256],name[128]={0},line[2048];
        snprintf(path,sizeof(path),"/proc/%.32s/comm",gpu_entry->d_name);
        FILE *f=fopen(path,"r");if(!f)continue;
         if(!fgets(name,sizeof(name),f)){fclose(f);continue;}fclose(f);
        if(!strstr(name,"render_service"))continue;
        snprintf(path,sizeof(path),"/proc/%.32s/maps",gpu_entry->d_name);
        f=fopen(path,"r");if(!f)continue;
        while(fgets(line,sizeof(line),f))if(strstr(line,"EGL")||strstr(line,"GLES")||strstr(line,"gallium")||strstr(line,"gbm")||strstr(line,"libc++"))printf("GPU885_MAP %s",line);
        fclose(f);
      }
      closedir(gpu_proc);
    }
    fflush(stdout);
    const char *paths[]={"/system/lib64/libEGL_mesa.so","/system/lib64/libEGL.so"};
    for(unsigned i=0;i<2;i++) {
      pid_t child=fork();if(child<0)die("GPU885 diagnostic fork");
      if(!child) {
        alarm(30);
        setenv("LD_LIBRARY_PATH","/system/lib64:/system/lib64/platformsdk:/system/lib64/chipset-sdk:/system/lib64/lab-softpipe-167",1);
        setenv("EGL_LOG_LEVEL","debug",1);
        execl("/system/lib64/lab-softpipe-167/gpu-frontend-probe","gpu-frontend-probe",paths[i],NULL);
        perror("GPU885 diagnostic exec");_exit(125);
      }
      int status=0;while(waitpid(child,&status,0)<0&&errno==EINTR){}
      printf("GPU885_CHILD path=%s status=%d\n",paths[i],status);fflush(stdout);
    }
    puts("GPU885_DONE desktop_not_tested=1");fflush(stdout);
'''
source = source.replace(anchor, anchor + probe)
remote = '/home/zoinve/.local/share/harmony-arm64-kvm-lab/command-probe-885'
subprocess.run(['ssh','matebook','mkdir '+remote],check=True)
out.mkdir()
(out/'init.c').write_text(source)
subprocess.run(['scp',str(out/'init.c'),str(base/'bounded-shell.c'),'matebook:'+remote+'/'],check=True)
subprocess.run(['ssh','matebook',f'gcc -static -O2 -Wall -Wextra -Werror {remote}/init.c -o {remote}/init'],check=True)
subprocess.run(['scp','matebook:'+remote+'/init',str(out/'init')],check=True)
script = r'''
from pathlib import Path
import shutil,gzip,hashlib,json
root=Path('/home/zoinve/harmony-virgl-883');out=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment/payload-885')
ram=root/'frontend-probe-885/ramroot';shutil.copytree(root/'system-overlay-883/ramroot',ram,symlinks=True)
shutil.copy2(out/'init',ram/'init');shutil.copy2(root/'frontend-probe-885/gpu-frontend-probe',ram/'gpu883-libs/gpu-frontend-probe')
def entry(name,data,mode,ino):
 n=name.encode()+b'\0';fields=[ino,mode,0,0,1,0,len(data),0,0,0,0,len(n),0]
 b=b'070701'+b''.join(f'{v:08x}'.encode() for v in fields)+n;b+=b'\0'*(-len(b)%4);b+=data;b+=b'\0'*(-len(data)%4);return b
raw=b'';files=[]
for i,p in enumerate(sorted(ram.rglob('*')),1):
 name=str(p.relative_to(ram))
 if p.is_symlink():data=str(p.readlink()).encode();mode=0o120777
 elif p.is_dir():data=b'';mode=0o040755
 else:data=p.read_bytes();mode=0o100755 if p.name in ['init','gpu-frontend-probe'] else 0o100444
 raw+=entry(name,data,mode,i);files.append(dict(path=name,mode=oct(mode),sha256=hashlib.sha256(data).hexdigest()))
raw+=entry('TRAILER!!!',b'',0,len(files)+1)
target=out/'initramfs.cpio.gz';assert not target.exists();target.write_bytes(gzip.compress(raw,mtime=0))
manifest=dict(sha256=hashlib.sha256(target.read_bytes()).hexdigest(),files=files,desktop_verified=False)
(out/'manifest.json').write_text(json.dumps(manifest,indent=2));print(manifest['sha256'])
'''
# Archive names must contain NUL bytes, not backslash-zero text.
script = script.replace("b'\\\\0'", "b'\\0'")
subprocess.run(['wsl','-d','Debian','--','python3','-'],input=script,text=True,check=True)
