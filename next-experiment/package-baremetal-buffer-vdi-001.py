"""Private experimental allocator bundle, original SDK handle ABI and Mesa003; no install."""
from pathlib import Path
import runpy
import subprocess

base=Path(__file__).resolve().parent
reference=Path('C:/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports/graphics/buffer_vdi.cpp').read_bytes()
vdi=runpy.run_path(str(base/'baremetal-buffer-vdi-001.py'))['build_source'](reference)
probe=(base/'gpu-allocator-probe.cpp').read_text()
for old,new in [
    ('#include <unistd.h>','#include <unistd.h>\n#include <fcntl.h>\n'+(base/'baremetal-freedreno-policy-001.h').read_text().replace('static int ', 'static inline int ')),
    ('    if (argc != 2) return 1;','    if (argc != 1) return 1;\n    (void)argv;\n    const char *allocator_path="libnative-buffer-vdi-001.so";'),
    ('argv[1]','allocator_path'),
    ('    Interface *allocator = create(); require(allocator, "factory");', '''    auto allocate_handle=reinterpret_cast<BufferHandle *(*)(uint32_t,uint32_t)>(dlsym(lib,"AllocateBufferHandle"));
    auto free_handle=reinterpret_cast<void (*)(BufferHandle *)>(dlsym(lib,"FreeBufferHandle"));
    require(allocate_handle && free_handle,"original SDK handle symbols");
    BufferHandle *abi=allocate_handle(2,3);
    require(abi && abi->reserveFds==2 && abi->reserveInts==3 && abi->fd==-1 && abi->reserve[0]==-1 && abi->reserve[1]==-1,"original SDK 56-byte handle ABI");
    free_handle(abi);
    printf("NATIVE_ALLOC001_HANDLE_ABI original_sdk=1 header_bytes=56 reserve_offset=48 reserve_fds=2 reserve_ints=3\\n");
    Interface *allocator = create(); require(allocator, "factory");'''),
    ('AuroraDrmDisplay drm = {}; require(!AuroraOpenDisplayDrm(&drm, 0), "DRM enumerate");','int render_fd=open("/dev/dri/renderD128", O_RDWR | O_CLOEXEC); require(render_fd>=0, "render node");'),
    ('gbm_create_device(drm.fd)','gbm_create_device(render_fd)'),
    ('renderer && strstr(renderer, "virgl")','freedreno_renderer_ok(renderer)'),
    ('sample ? 1920U : 13U, sample ? 1080U : 7U','sample ? 1600U : 13U, sample ? 2560U : 7U'),
    ('require(!allocator->Unmap(*handle), "unmap");','/* Mapping kept live to independently verify flush and invalidation. */'),
    ('glBindFramebuffer(GL_FRAMEBUFFER, 0); glDeleteFramebuffers(1, &fbo);', '''glClearColor(0.75f, 0.25f, 0.5f, 1.0f); glClear(GL_COLOR_BUFFER_BIT); glFinish();
        require(glGetError()==GL_NO_ERROR && !allocator->InvalidateCache(*handle), "invalidate after GPU clear");
        printf("NATIVE_ALLOC001_GPU_TO_CPU sample=%d rgba=%u,%u,%u,%u\\n", sample,pixels[0],pixels[1],pixels[2],pixels[3]);
        require(pixels[0]==191 && pixels[1]==64 && pixels[2]==128 && pixels[3]==255, "GPU-to-CPU pixels");
        require(!allocator->Unmap(*handle), "unmap");
        glBindFramebuffer(GL_FRAMEBUFFER, 0); glDeleteFramebuffers(1, &fbo);'''),
    ('close(drm.fd)','close(render_fd)'),('GPU903_','NATIVE_ALLOC001_')]:
    assert old in probe,old
    probe=probe.replace(old,new)
assert 'AuroraOpenDisplayDrm(' not in probe and 'virgl' not in probe
payload='vdi='+repr(vdi)+'\nprobe='+repr(probe)+'\n'+r'''
from pathlib import Path
import hashlib,json,subprocess,shutil,re,tarfile,os
root=Path('/home/zoinve/harmony-virgl-883');project=Path('/mnt/d/lab/HarmonyOSForMatebookego')
work=root/'baremetal-buffer-vdi-001';report=project/'reports/baremetal-buffer-vdi-package-001'
assert not work.exists() and not report.exists();work.mkdir();report.mkdir()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
ref=Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports/graphics')
reference_files={str(p):sha(p) for p in ref.rglob('*') if p.is_file()}
shutil.copytree(ref/'include',work/'include');(work/'vdi.cpp').write_text(vdi);(work/'probe.cpp').write_text(probe)
bundle=work/'bundle';libs=bundle/'lib';libs.mkdir(parents=True)
fence=json.loads((project/'reports/baremetal-freedreno-fence-package-002/package.json').read_text())
fence_root=root/'baremetal-freedreno-fence-002/bundle'
for row in fence['files']:
 if row['path']=='probe':continue
 src=fence_root/row['path'];assert sha(src)==row['sha256'] and src.stat().st_size==row['bytes']
 dest=bundle/row['path'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
(libs/'libc.so').symlink_to('ld-musl-aarch64.so.1')
sdk=json.loads((project/'reports/baremetal-identity-ipc-callback-012/result.json').read_text())
available={Path(row['name']).name:row for row in sdk['ram_files'] if Path(row['name']).name not in ['probe','loader']}
handle=root/'baremetal-buffer-handle-audit-001/original-2.so'
assert sha(handle)=='9c3ab7c3c83e074d0238814153752656c28b56202f833ad07f34b2cffd640912'
shutil.copyfile(handle,libs/'libbuffer_handle.z.so')
def needed(p):
 text=subprocess.check_output(['aarch64-linux-gnu-readelf','-d',str(p)],text=True)
 return re.findall(r'\(NEEDED\).*\[([^]]+)\]',text)
pending=[libs/'libbuffer_handle.z.so'];visited=set()
while pending:
 p=pending.pop()
 if p.name in visited:continue
 visited.add(p.name)
 for name in needed(p):
  dst=libs/name
  if not dst.exists():
   row=available[name];src=Path(row['path']);assert sha(src)==row['sha256'] and src.stat().st_size==row['bytes']
   shutil.copyfile(src,dst)
  if name!='libc.so':pending.append(dst)
prefix=root/'prefix/system';includes=['-I'+str(work),'-I'+str(work/'include'),'-I'+str(prefix/'include'),'-I'+str(prefix/'include/libdrm')]
common=[str(root/'toolchain/ohos-cxx'),'-O2','-std=c++17','-fno-emulated-tls','-Wall','-Wextra','-Werror',*includes]
link=['-L'+str(libs),'-Wl,-rpath,$ORIGIN/lib:$ORIGIN','-Wl,-rpath-link,'+str(libs)]
commands=[[*common,'-shared','-fPIC',str(work/'vdi.cpp'),*link,'-lgbm','-ldrm','-l:libbuffer_handle.z.so','-Wl,--no-undefined,-soname,libnative-buffer-vdi-001.so','-o',str(libs/'libnative-buffer-vdi-001.so')],
          [*common,str(work/'probe.cpp'),*link,'-lEGL','-lGLESv2','-lgbm','-ldrm','-ldl','-o',str(bundle/'probe')]]
for i,args in enumerate(commands):
 r=subprocess.run(args,capture_output=True,text=True,timeout=90)
 (report/('compile-'+str(i)+'.stdout')).write_text(r.stdout);(report/('compile-'+str(i)+'.stderr')).write_text(r.stderr)
 assert r.returncode==0,r.stderr
files=[]
for p in sorted(bundle.rglob('*')):
 if not p.is_file() or p.is_symlink():continue
 header=subprocess.check_output(['aarch64-linux-gnu-readelf','-h',str(p)],text=True);assert 'AArch64' in header
 for name in needed(p):assert (libs/name).exists(),(str(p),name)
 p.chmod(0o555);files.append(dict(path=str(p.relative_to(bundle)),bytes=p.stat().st_size,sha256=sha(p)))
assert reference_files=={str(p):sha(p) for p in ref.rglob('*') if p.is_file()}
manifest=dict(files=files,commands=commands,vdi_source_sha256=sha(work/'vdi.cpp'),probe_source_sha256=sha(work/'probe.cpp'),original_sdk_handle_sha256=sha(handle),all_needed_libraries_present=True,reference_files_unchanged=True,gpu_execution_verified=False,installed=False,desktop_verified=False)
(bundle/'manifest.json').write_text(json.dumps(manifest,indent=2))
archive=work/'bundle.tar.gz'
with tarfile.open(archive,'w:gz') as tar:
 for p in sorted(bundle.rglob('*')):tar.add(p,arcname=str(p.relative_to(bundle)),recursive=False)
manifest.update(archive_sha256=sha(archive),archive_bytes=archive.stat().st_size)
(work/'package.json').write_text(json.dumps(manifest,indent=2));(report/'package.json').write_text(json.dumps(manifest,indent=2));shutil.copyfile(archive,report/'bundle.tar.gz')
print(json.dumps(dict(files=len(files),archive_bytes=manifest['archive_bytes'],archive_sha256=manifest['archive_sha256'],gpu_execution_verified=False,reference_files_unchanged=True)))
'''
compile(payload,'native-buffer-vdi-package001','exec')
if __name__=='__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=240).returncode)
