"""Package original OHOS token API/runtime with guarded real-kernel regressions."""
from pathlib import Path
import runpy
import subprocess

base=Path(__file__).resolve().parent
source=runpy.run_path(str(base/'prepare-baremetal-identity-nested-005.py'))['source']
anchor='    close(binder);close(fd);'
assert source.count(anchor)==1
source=source.replace(anchor,'''    pid_t sdk_child=fork();require(sdk_child>=0,"fork original SDK runtime test");
    if(!sdk_child) {
        close(binder);close(fd);
        execl("/sdk/loader","/sdk/loader","--library-path","/sdk","/sdk/probe",(char *)NULL);
        _exit(92);
    }
    require(child_status(sdk_child),"unmodified original SDK token APIs pass on candidate kernel");
    uint64_t after_sdk=0;
    require(ioctl(fd,SELF_GET,&after_sdk)==0&&after_sdk==value,"SDK exec child does not mutate init self token");
    require(ioctl(fd,FIRST_GET,&after_sdk)==0&&after_sdk==first,"SDK exec child does not mutate init first token");
    close(binder);close(fd);''')
source=source.replace('IDENTITY005_','IDENTITY006_')
sdk_source=(base/'baremetal-identity-sdk-api-006.c').read_text()
payload='source='+repr(source)+'\nsdk_source='+repr(sdk_source)+'\n'+r'''
from pathlib import Path
import hashlib,json,re,shutil,subprocess
root=Path('/home/zoinve/harmony-virgl-883');work=root/'baremetal-identity-sdk-006'
local=Path('/mnt/d/lab/HarmonyOSForMatebookego/reports/baremetal-identity-sdk-006')
assert not work.exists() and not local.exists();work.mkdir();local.mkdir();sdk=work/'sdk';sdk.mkdir()
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(args,name):
 r=subprocess.run(args,capture_output=True,text=True,timeout=60)
 (local/(name+'.stdout')).write_text(r.stdout);(local/(name+'.stderr')).write_text(r.stderr)
 assert r.returncode==0,r.stderr
 return r.stdout
loader=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment/official-gpu-probe-924/official-loader.so')
assert sha(loader)=='f7947b746dc4169677321b18ee77e4f4f158fde75762b2d9a3ae107b277c0181'
shutil.copyfile(loader,sdk/'loader')
token=root/'baremetal-sdk-identity-inspect-001/libtokensetproc_shared.z.so'
shutil.copyfile(token,sdk/token.name)
system='/mnt/d/Download/pc_all_arm/system.img'
run(['debugfs','-R','dump /system/lib64/chipset-sdk-sp/libsec_shared.z.so '+str(sdk/'libsec_shared.z.so'),system],'extract-sec')
run(['debugfs','-R','dump /system/lib64/platformsdk/libtokensetproc_shared.z.so '+str(work/'original-token.so'),system],'verify-original-token')
assert (work/'original-token.so').read_bytes()==token.read_bytes()
(work/'init.c').write_text(source);(work/'sdk-probe.c').write_text(sdk_source)
run(['aarch64-linux-gnu-gcc','-static','-O2','-Wall','-Wextra','-Werror',str(work/'init.c'),'-o',str(work/'init')],'compile-init')
run([str(root/'toolchain/ohos-cc'),'-O2','-Wall','-Wextra','-Werror',str(work/'sdk-probe.c'),'-o',str(sdk/'probe')],'compile-sdk')
ram_files=[];dynamic={}
for name in ['loader','probe','libtokensetproc_shared.z.so','libsec_shared.z.so']:
 p=sdk/name;elf=run(['aarch64-linux-gnu-readelf','-h',str(p)],'elf-'+name);assert 'AArch64' in elf
 d=run(['aarch64-linux-gnu-readelf','-d',str(p)],'dynamic-'+name)
 needed=re.findall(r'Shared library: \[([^]]+)\]',d)
 assert all(n in ['libc.so','libsec_shared.z.so'] for n in needed),(name,needed)
 dynamic[name]=needed
 ram_files.append(dict(name='sdk/'+name,path=str(p),bytes=p.stat().st_size,sha256=sha(p)))
report=dict(path=str(work/'init'),bytes=(work/'init').stat().st_size,sha256=sha(work/'init'),source_sha256=hashlib.sha256(source.encode()).hexdigest(),ram_files=ram_files,dynamic_dependencies=dynamic,original_token_library_verified=True,original_loader_sha256=sha(sdk/'loader'),runtime_verified=False,images_modified=False)
(work/'result.json').write_text(json.dumps(report,indent=2));(local/'result.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
'''
compile(payload,'prepare-sdk-006','exec')
if __name__=='__main__':
    result=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(result.returncode)
