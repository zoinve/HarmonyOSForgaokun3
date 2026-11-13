"""Fresh 890: diagnostic-thread hook-table provenance; rendering unchanged."""
from pathlib import Path
import subprocess

base = Path(__file__).resolve().parent
out = base / 'payload-890'
assert not out.exists()
out.mkdir()
script = r'''
from pathlib import Path
import shutil,subprocess,gzip,hashlib,json
root=Path('/home/zoinve/harmony-virgl-883')
work=root/'hook-probe-890';work.mkdir()
ram=work/'ramroot';shutil.copytree(root/'executable-probe-889/ramroot',ram,symlinks=True)
probe=(root/'dispatch-probe-888/probe.c').read_text()
probe=probe.replace('#include <dlfcn.h>','#include <dlfcn.h>\n#include <pthread.h>')
anchor='    printf("GPU888_DIRECT_GL renderer=%s\\n",native?native:"NULL");'
assert probe.count(anchor)==1
probe=probe.replace(anchor,anchor+r"""
    void *(*tls_table)(void)=dlsym(lib,"_ZN4OHOS20ThreadPrivateDataCtl14GetGlHookTableEv");
    void *(*get_table)(void)=dlsym(lib,"GetHookTable");
    unsigned (*get_key)(void)=dlsym(lib,"GetHookTableKey");
    void *before=tls_table?tls_table():NULL;
    unsigned key=get_key?get_key():~0u;
    void *specific=key!=~0u?pthread_getspecific(key):NULL;
    void *table=get_table?get_table():NULL;
    printf("GPU890_HOOK before=%p table=%p key=%u specific=%p\n",before,table,key,specific);
    void *entry=NULL;
    if(table)memcpy(&entry,(const char*)table+0x2090,sizeof(entry));
    Dl_info slot_info={0};
    int slot_known=entry?dladdr(entry,&slot_info):0;
    printf("GPU890_SLOT offset=2090 entry=%p library=%s symbol=%s\n",entry,
        slot_known&&slot_info.dli_fname?slot_info.dli_fname:"NULL",
        slot_known&&slot_info.dli_sname?slot_info.dli_sname:"NULL");
    void *bridge=dlopen("/system/lib64/libEGL_mesa.so",RTLD_NOW|RTLD_LOCAL);
    __typeof__(&eglGetProcAddress) bridge_proc=bridge?dlsym(bridge,"eglGetProcAddress"):NULL;
    void *real_string=bridge_proc?(void*)bridge_proc("glGetString"):NULL;
    Dl_info real_info={0};int real_known=real_string?dladdr(real_string,&real_info):0;
    printf("GPU890_REAL_PROC entry=%p library=%s symbol=%s\n",real_string,
        real_known&&real_info.dli_fname?real_info.dli_fname:"NULL",
        real_known&&real_info.dli_sname?real_info.dli_sname:"NULL");
""")
(work/'probe.c').write_text(probe)
prefix=root/'prefix/system'
subprocess.run([str(root/'toolchain/ohos-cc'),'-O2','-Wall','-Wextra','-Werror',
 '-I'+str(prefix/'include'),str(work/'probe.c'),'-ldl','-lpthread','-o',str(work/'gpu-frontend-probe')],check=True)
shutil.copy2(work/'gpu-frontend-probe',ram/'gpu883-libs/gpu-frontend-probe')
out=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment/payload-890')
'''
original = (base / 'build-gpu-frontend-payload.py').read_text()
archive = 'def entry(' + original.split('def entry(', 1)[1].split("'''", 1)[0]
subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
               input=script + archive, text=True, check=True)
