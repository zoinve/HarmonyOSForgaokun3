"""Exercise the real command diagnostic after persistent capture closes fd 199."""
from pathlib import Path
import runpy,subprocess,sys
builder=Path(__file__).with_name(sys.argv[1] if len(sys.argv)>1 else 'build-commercial-native-003.py')
p=runpy.run_path(str(builder));s=p['inner']
fn=s[s.index('static void commercial_command002'):s.index('static void commercial_early_kernel002')]
c=r'''
#define _GNU_SOURCE
#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <sys/wait.h>
static int commercial_diag_fd003;
'''+fn+r'''
int main(void){
 char name[]="/tmp/commercial-capture-test-XXXXXX";int f=mkstemp(name);unlink(name);
 if(f<0 || dup2(f,199)<0)return 2;
 commercial_diag_fd003=fcntl(199,F_DUPFD_CLOEXEC,200);close(199);
 char *args[]={"/bin/echo","COMMERCIAL_CAPTURE_TEST",NULL};commercial_command002(args);
 char b[4096]={0};lseek(f,0,SEEK_SET);ssize_t n=read(f,b,sizeof(b)-1);
 close(commercial_diag_fd003);close(f);
 if(n<=0 || !strstr(b,"COMMERCIAL_CAPTURE_TEST") || !strstr(b,"status=0")){
  fprintf(stderr,"FAIL: diagnostic output lost after collector closes original descriptors\n");return 1;
 }
 puts("PASS: real diagnostic subprocess writes to retained private descriptor after fd 199 is closed");
}
'''
payload="from pathlib import Path\nimport subprocess\np=Path('/home/zoinve/harmony-virgl-883/commercial-capture-003-tests');p.mkdir(exist_ok=True)\n"
payload+='(p/"capture.c").write_text('+repr(c)+')\n'
payload+="subprocess.run(['gcc','-O2','-Wall','-Wextra','-Werror',str(p/'capture.c'),'-o',str(p/'capture')],check=True)\nraise SystemExit(subprocess.run([str(p/'capture')]).returncode)\n"
raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True).returncode)
