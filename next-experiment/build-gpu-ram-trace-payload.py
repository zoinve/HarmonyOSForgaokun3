"""Fresh 893: RAM-only per-process tracing, without service permission changes."""
from pathlib import Path
import subprocess

base = Path(__file__).resolve().parent
out = base / 'payload-893'
assert not out.exists()
source = (base / 'payload-887/init.c').read_text()
anchor = '    if(chdir("/newroot") || mount(".","/",NULL,MS_MOVE,NULL) || chroot(".") || chdir("/")) die("switch root mount");'
assert source.count(anchor) == 1
source = source.replace(anchor, '''    if(mkdir("/newroot/dev/gpu893-trace",01777)) die("GPU893 mkdir");
    if(chmod("/newroot/dev/gpu893-trace",01777)) die("GPU893 chmod new RAM directory");
''' + anchor)
anchor = '    ui_snapshot();'
assert source.count(anchor) == 1
source = source.replace(anchor, '''    DIR *traces=opendir("/dev/gpu893-trace");
    if(traces) {
      struct dirent *entry;unsigned count=0;
      while((entry=readdir(traces)) && count<32) {
        if(entry->d_name[0]=='.')continue;
        char path[320];snprintf(path,sizeof(path),"/dev/gpu893-trace/%.255s",entry->d_name);
        ui_read(path);count++;
      }
      closedir(traces);
    }
''' + anchor)
anchor = 'if(n<=0)continue;'
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + '''
        char *base_name=strrchr(name,'/');
        if(base_name)memmove(name,base_name+1,strlen(base_name+1)+1);
''')
source = source.replace('count<12', 'count<64')
remote = '/home/zoinve/.local/share/harmony-arm64-kvm-lab/command-probe-893'
subprocess.run(['ssh', 'matebook', 'mkdir ' + remote], check=True)
out.mkdir()
(out/'init.c').write_text(source)
subprocess.run(['scp',str(out/'init.c'),str(base/'bounded-shell.c'),'matebook:'+remote+'/'],check=True)
subprocess.run(['ssh','matebook',f'gcc -static -O2 -Wall -Wextra -Werror {remote}/init.c -o {remote}/init'],check=True)
subprocess.run(['scp','matebook:'+remote+'/init',str(out/'init')],check=True)
original = (base/'build-gpu-present-trace-payload.py').read_text()
script = original.split("script = r'''",1)[1].split("'''",1)[0]
script = script.replace('present-trace-892','ram-trace-893').replace('payload-892','payload-893')
script = script.replace("root/'gles-alias-probe-891/ramroot'", "root/'present-trace-892/ramroot'")
script = script.replace('helper="""', 'helper="""\n#include <fcntl.h>\n#include <cerrno>')
script = script.replace('/data/local/tmp/gpu892-%ld.log','/dev/gpu893-trace/gpu893-%ld.log')
script = script.replace(' FILE *f=std::fopen(path,"a");if(!f)return;', ''' int saved_errno=errno;
 int fd=open(path,O_WRONLY|O_CREAT|O_APPEND|O_CLOEXEC|O_NOFOLLOW,0600);
 if(fd<0){errno=saved_errno;return;}
 FILE *f=fdopen(fd,"a");if(!f){close(fd);errno=saved_errno;return;}''')
script = script.replace(' std::fclose(f);',' std::fclose(f);errno=saved_errno;')
script += "\nshutil.copy2(out/'init',ram/'init')\n"
archive_source = (base/'build-gpu-frontend-payload.py').read_text()
archive = 'def entry(' + archive_source.split('def entry(',1)[1].split("'''",1)[0]
subprocess.run(['wsl','-d','Debian','--','python3','-'],input=script+archive,text=True,check=True)
