"""Real pipe/file tests; never launch target services or touch hardware."""
from pathlib import Path
import subprocess
header=Path(__file__).with_name('native-continuous-capture-030.h')
assert header.exists(),'missing bounded continuous capture helper'
code=r'''
from pathlib import Path
import tempfile,subprocess
h=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment/native-continuous-capture-030.h')
src=r"""
#define _GNU_SOURCE
#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include "native-continuous-capture-030.h"
int main(void){
 for(int limited=0;limited<2;++limited){
  char name[]="/var/tmp/capture030-XXXXXX";int out=mkstemp(name);assert(out>=0);unlink(name);
  int p[2];assert(!pipe(p));assert(write(p[1],"abcdefghij",10)==10);close(p[1]);
  int status=capture_stream030(p[0],out,limited?5:100);
  assert(status==(limited?1:0));assert(lseek(out,0,SEEK_END)==(limited?5:10));
  lseek(out,0,SEEK_SET);char b[20]={0};assert(read(out,b,sizeof(b))==(limited?5:10));
  assert(!memcmp(b,"abcdefghij",limited?5:10));close(p[0]);close(out);
 }
 /* A quiet interval must not stop the reader or lose a later event. */
 char name[]="/var/tmp/capture030-late-XXXXXX";int out=mkstemp(name);assert(out>=0);unlink(name);
 int p[2];assert(!pipe(p));pid_t writer=fork();assert(writer>=0);
 if(!writer){close(p[0]);sleep(3);assert(write(p[1],"late-event",10)==10);close(p[1]);_exit(0);}
 close(p[1]);assert(capture_stream030(p[0],out,100)==0);close(p[0]);
 int state=0;assert(waitpid(writer,&state,0)==writer && state==0);
 assert(lseek(out,0,SEEK_END)==10);lseek(out,0,SEEK_SET);char b[11]={0};
 assert(read(out,b,10)==10 && !strcmp(b,"late-event"));close(out);
 return 0;
}
"""
with tempfile.TemporaryDirectory(prefix='capture030-') as t:
 p=Path(t);(p/'test.c').write_text(src)
 subprocess.run(['gcc','-std=gnu11','-O2','-Wall','-Wextra','-Werror','-I'+str(h.parent),str(p/'test.c'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
print('PASS real pipe/file byte preservation, EOF fsync, exact capacity limit, late event after idle poll')
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=code,text=True,timeout=60).returncode)
