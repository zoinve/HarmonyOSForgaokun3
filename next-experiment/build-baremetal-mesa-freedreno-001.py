"""Offline OHOS Freedreno build in fresh directories; no installation or device access."""
from pathlib import Path
import subprocess

base = Path(__file__).resolve().parent.parent
out = base / 'reports/baremetal-mesa-freedreno-build-001'

payload = r'''
from pathlib import Path
import hashlib,json,os,shutil,subprocess,time
root=Path('/home/zoinve/harmony-virgl-883')
work=root/'baremetal-mesa-freedreno-001'
report=Path('/mnt/d/lab/HarmonyOSForMatebookego/reports/baremetal-mesa-freedreno-build-001')
source=root/'sources/mesa-mirror-c185b4a7b0ff052f556dff1b3849a9c9c6115640'
assert not work.exists(), 'Preserve numbered builds, including partial ones'
assert source.is_dir() and shutil.disk_usage(root).free > 8*1024**3
def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def tree_hashes(path):
    rows={}
    for directory,dirs,files in os.walk(path):
        dirs[:]=sorted(d for d in dirs if d!='.git')
        for name in sorted(files):
            p=Path(directory)/name
            rows[str(p.relative_to(path))]=('symlink:'+os.readlink(p)) if p.is_symlink() else sha(p)
    return rows
before=tree_hashes(source)
legacy=root/'prefix/system/lib64/lab-virgl883'
protected={str(p):sha(p) for p in legacy.rglob('*') if p.is_file() and not p.is_symlink()}
work.mkdir();stage=work/'stage';build=work/'build'
cross=work/'ohos-cross.ini'
original=(root/'toolchain/ohos-cross.ini').read_text()
assert original.count('-Wl,-rpath,/system/lib64/lab-virgl883')==2
cross.write_text(original.replace('-Wl,-rpath,/system/lib64/lab-virgl883',
                                 '-Wl,-rpath,/system/lib64/lab-freedreno001'))
(report/'source-before.json').write_text(json.dumps(before,sort_keys=True))
result=dict(work=str(work),mesa_version='25.0.1',gallium_driver='freedreno',kernel_driver='msm',
    target='aarch64-linux-ohos',downloads_allowed=False,device_accessed=False,
    original_images_modified=False,boot_entries_modified=False,reboot_requested=False,
    runtime_gpu_rendering_verified=False,harmony_desktop_verified=False,build_success=False)
start=time.monotonic()
def run(args,name,timeout,env=None):
    result.setdefault('commands',[]).append(dict(command=args,log=name))
    with (work/name).open('xb') as log:
        p=subprocess.run(args,stdout=log,stderr=subprocess.STDOUT,timeout=timeout,env=env)
    shutil.copyfile(work/name,report/name)
    assert p.returncode==0, name+' failed; retain numbered directory and inspect log'
try:
    includes='-I'+str(root/'prefix/system/include')+' -fno-emulated-tls'
    args=['meson','setup',str(build),str(source),'--cross-file',str(cross),
          '--wrap-mode=nofallback','--buildtype=release','--prefix=/system',
          '--libdir=lib64/lab-freedreno001','-Dauto_features=disabled',
          '-Dgallium-drivers=freedreno','-Dfreedreno-kmds=msm','-Dvulkan-drivers=',
          '-Dplatforms=','-Dglx=disabled','-Dglvnd=disabled','-Degl=enabled',
          '-Dgles1=enabled','-Dgles2=enabled','-Dgbm=enabled','-Dshared-glapi=enabled',
          '-Dllvm=disabled','-Dshader-cache=disabled','-Dgallium-va=disabled',
          '-Dvideo-codecs=','-Dc_args='+includes,'-Dcpp_args='+includes]
    run(args,'configure.log',300)
    options=json.loads((build/'meson-info/intro-buildoptions.json').read_text())
    values={x['name']:x['value'] for x in options}
    assert values['gallium-drivers']==['freedreno'] and values['freedreno-kmds']==['msm']
    assert values['libdir']=='lib64/lab-freedreno001'
    (report/'build-options.json').write_text(json.dumps(options,indent=2))
    run(['ninja','-C',str(build),'-j4'],'build.log',2400)
    run(['meson','install','-C',str(build),'--no-rebuild','--destdir',str(stage)],'stage.log',180)
    artifacts=[]
    for p in sorted(stage.rglob('*')):
        if not p.is_file() or p.is_symlink():continue
        row=dict(path=str(p.relative_to(stage)),bytes=p.stat().st_size,sha256=sha(p))
        with p.open('rb') as f:magic=f.read(4)
        if magic==b'\x7fELF':
            header=subprocess.check_output(['readelf','-h',str(p)],text=True,timeout=15)
            assert 'AArch64' in header,str(p)
            row['dynamic']=subprocess.check_output(['readelf','-d',str(p)],text=True,timeout=15)
        artifacts.append(row)
    assert any('libEGL.so' in x['path'] for x in artifacts)
    assert any('libGLESv2.so' in x['path'] for x in artifacts)
    assert any('libgbm.so' in x['path'] for x in artifacts)
    assert any('gallium' in x['path'] or 'msm_dri.so' in x['path'] for x in artifacts)
    result['artifacts']=artifacts
    result['build_success']=True
except Exception as error:
    result['error']=repr(error)
    raise
finally:
    for name in ('configure.log','build.log','stage.log'):
        if (work/name).exists():shutil.copyfile(work/name,report/name)
    result['source_files_verified_unchanged']=tree_hashes(source)==before
    result['legacy_prefix_files_verified_unchanged']=all(Path(p).is_file() and sha(Path(p))==digest for p,digest in protected.items())
    result['elapsed_seconds']=time.monotonic()-start
    (work/'result.json').write_text(json.dumps(result,indent=2))
    (report/'result.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2),flush=True)
    assert result['source_files_verified_unchanged'] and result['legacy_prefix_files_verified_unchanged']
'''

if __name__ == '__main__':
    compile(payload, 'freedreno-build-001', 'exec')
    assert not out.exists(), 'Preserve existing reports'
    out.mkdir()
    subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=payload,
                   text=True, check=True, timeout=3100)
