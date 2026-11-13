from pathlib import Path
import subprocess
p=Path(__file__).with_name('native-qca-probe-021.c')
assert p.exists(),'missing real QCA HCI reset probe'
code=r'''
import pathlib,subprocess,tempfile
src=pathlib.Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment/native-qca-probe-021.c')
with tempfile.TemporaryDirectory(prefix='qca-parser-021-') as tmp:
 p=pathlib.Path(tmp);test=p/'test.c'
 test.write_text('#define main probe_main\n#include "'+str(src)+'"\n#undef main\n#include <assert.h>\nint main(void){unsigned char ok[]={4,14,4,1,3,12,0};unsigned char bad[]={4,14,4,1,3,12,1};assert(reset_reply(ok,sizeof(ok))==1);assert(reset_reply(bad,sizeof(bad))==-1);assert(reset_reply(ok,6)==0);ok[4]=4;assert(reset_reply(ok,sizeof(ok))==0);return 0;}')
 subprocess.run(['gcc','-O2','-Wall','-Wextra','-Werror',str(test),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
print('HCI reset reply parser: success, controller failure, truncation and unrelated opcode verified; no hardware access')
'''
raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=code,text=True).returncode)
