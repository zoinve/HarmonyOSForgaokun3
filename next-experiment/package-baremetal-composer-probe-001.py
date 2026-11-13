"""Private extracted-method experiment; not the full composer or its HDI ABI."""
from pathlib import Path
import runpy
import subprocess

base=Path(__file__).resolve().parent
sources=runpy.run_path(str(base/'baremetal-composer-bridge-001.py'))['build_sources']()
parent=runpy.run_path(str(base/'package-baremetal-freedreno-ipc-002.py'))
payload=parent['payload']
head,separator,tail=payload.partition('\nheader=')
namespace={};exec(compile(head,'probe-source-literal','exec'),namespace)
source=namespace['source']
anchor='static int consume001(void)'
assert source.count(anchor)==1
source=source.replace(anchor,'''extern int composer_accept001(int,int,uint32_t,uint32_t,uint32_t);
extern int composer_borrow001(void);
extern int composer_clear001(void);
'''+anchor)
start=source.index('    struct pollfd pending=')
end=source.index('    int render=open(',start)
source=source[:start]+'''    require(composer_accept001(fds[0],fds[1],packet.width,packet.height,packet.stride)==0,
            "actual reference composer accepts transferred buffer and waits fence");
    int retained=composer_borrow001();
    require(retained>=0 && retained!=fds[0] && (fcntl(retained,F_GETFD)&FD_CLOEXEC),
            "actual reference composer retained duplicate");
    require(fcntl(fds[1],F_GETFD)>=0,"composer leaves caller fence owned");
    close(fds[0]);close(fds[1]);fds[0]=retained;
    int polled=1; /* Actual reference wait_fence succeeded, not an independent poll measurement. */
'''+source[end:]
anchor='    close(fds[0]); /* Imported BO must retain its own reference. */'
assert source.count(anchor)==1
source=source.replace(anchor,'''    require(composer_clear001()==0 && composer_borrow001()==-1,"actual composer clears held FD");
    errno=0;require(fcntl(retained,F_GETFD)==-1 && errno==EBADF,"composer held FD closed after import");
    puts("COMPOSER001_CONTRACT actual_reference_methods=1 caller_fds_closed=1 held_fd_closed=1 no_init_display=1 no_commit=1");''')
source=source.replace('IPC002_','COMPOSER001_').replace('fence_poll=%d','reference_fence_wait_success=%d')
payload='source='+repr(source)+'\nbridge_sources='+repr(sources)+separator+tail
payload=payload.replace('baremetal-freedreno-ipc-package-002','baremetal-composer-probe-package-001').replace("work=root/'baremetal-freedreno-ipc-002'","work=root/'baremetal-composer-probe-001'")
anchor="r=subprocess.run(args,capture_output=True,text=True,timeout=60)"
assert payload.count(anchor)==1
payload=payload.replace(anchor,'''for name,text in bridge_sources.items():(work/name).write_text(text)
bridge_args=[str(root/'toolchain/ohos-cxx'),'-std=c++17','-O2','-shared','-fPIC','-Wall','-Wextra','-Werror',
 '-Wno-misleading-indentation','-fno-emulated-tls','-I'+str(work),str(work/'bridge.cpp'),
 '-Wl,--no-undefined,-soname,libcomposer-methods-001.so','-o',str(libs/'libcomposer-methods-001.so')]
r=subprocess.run(bridge_args,capture_output=True,text=True,timeout=60)
(report/'bridge-compile.stdout').write_text(r.stdout);(report/'bridge-compile.stderr').write_text(r.stderr);r.check_returncode()
args[1:1]=['-L'+str(libs),'-l:libcomposer-methods-001.so','-Wl,-rpath-link,'+str(libs)]
'''+anchor)
payload=payload.replace('manifest=dict(files=rows,',"manifest=dict(extracted_methods_only=True,full_hdi_abi_verified=False,bridge_source_sha256=sha(work/'bridge.cpp'),bridge_build_command=bridge_args,files=rows,")
compile(payload,'composer-probe001-package','exec')
if __name__=='__main__':
    out=base.parent/'reports/baremetal-composer-probe-package-001'
    assert not out.exists();out.mkdir()
    subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,check=True,timeout=180)
