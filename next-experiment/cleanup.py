"""One-time, user-authorized cleanup of enumerated task artifacts only."""
from pathlib import Path
import json, re, shutil, subprocess, time, os, stat

project = Path(__file__).resolve().parent.parent
temp = Path('C:/Users/39255/AppData/Local/Temp/opencode')
report = project / 'next-experiment/cleanup-result.json'
assert not report.exists()

linux_script = r'''
from pathlib import Path
import json,shutil,os,hashlib
root=Path(ROOT)
keep=set(KEEP)
assert root.is_dir() and not root.is_symlink()
for p in Path('/sys/block').glob('loop*/loop/backing_file'):
 try: backing=p.read_text().strip()
 except OSError:continue
 assert not backing.startswith(str(root)+'/'),('mounted loop backing',backing)
for line in Path('/proc/self/mountinfo').read_text().splitlines():
 fields=line.split()
 assert not fields[4].startswith(str(root)+'/'),('mounted subtree',fields[4])
if 'system-868' in keep:
 c=json.loads((root/'system-868/config.json').read_text())
 required=[x['path'] for x in c['disks']]+[x['remote'] for x in c['inputs']]
 required.append(str(root/'disks-744/userdata-analysis.img'))
 for value in required:
  p=Path(value);assert p.is_file() and p.relative_to(root).parts[0] in keep,value
 for p in Path('/proc').iterdir():
  if not p.name.isdigit():continue
  try:args=(p/'cmdline').read_bytes().split(b'\0')
  except OSError:continue
  if not args or not Path(os.fsdecode(args[0])).name.startswith('qemu-system-'):continue
  assert any(str(root/'system-868').encode() in a for a in args),'unexpected QEMU'
else:
 for p in Path('/proc').iterdir():
  if not p.name.isdigit():continue
  try:
   exe=(p/'exe').resolve()
   cwd=(p/'cwd').resolve()
  except OSError:continue
  assert not str(exe).startswith(str(root)+'/') and not str(cwd).startswith(str(root)+'/'),('active build process',p.name)
targets=[p for p in root.iterdir() if p.name not in keep]
stats={str(p):(p.stat().st_size,p.stat().st_mtime_ns) for p in root.iterdir() if p.is_file() and p.name in keep}
before=shutil.disk_usage(root).free
deleted=[]
for p in targets:
 assert p.parent==root and p.name not in keep
 if p.is_symlink() or not p.is_dir():p.unlink()
 else:shutil.rmtree(p)
 deleted.append(p.name)
for path,value in stats.items():
 p=Path(path);assert (p.stat().st_size,p.stat().st_mtime_ns)==value
assert {p.name for p in root.iterdir()}==keep
hashes={}
if 'system-868' in keep:
 expected={x['path']:x['sha256'] for x in c['disks'] if x['readonly']}
 expected[str(root/'disks-744/userdata-analysis.img')]='667cbbb0658558eb2a80d13f61f5bbc6ce54e4bbd8f5c0a6817e881566ac2f56'
 for path,value in expected.items():
  with Path(path).open('rb') as f:hashes[path]=hashlib.file_digest(f,'sha256').hexdigest()
  assert hashes[path]==value,path
print(json.dumps(dict(root=str(root),deleted=deleted,free_before=before,free_after=shutil.disk_usage(root).free,retained=sorted(keep),protected_hashes=hashes)))
'''

def linux_cleanup(command, root, keep):
    source = linux_script.replace('ROOT', repr(root)).replace('KEEP', repr(keep))
    r = subprocess.run(command, input=source, capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, r.stderr + r.stdout
    return json.loads(r.stdout)

checkpoint=report.with_name('cleanup-progress.json')
results = json.loads(checkpoint.read_text()) if checkpoint.exists() else {}
for name, command, root, keep in [
    ('matebook',['ssh', 'matebook', 'sudo -n python3 -'],'/home/zoinve/.local/share/harmony-arm64-kvm-lab',['disks-744', 'system-868', 'direct-observe-864']),
    ('wsl',['wsl', '-d', 'Debian', '--', 'python3', '-'],'/home/zoinve/.local/share/harmony-arm64-kernel-lab',[])]:
    if name not in results:
        results[name]=linux_cleanup(command,root,keep)
        checkpoint.write_text(json.dumps(results,indent=2))

keep_temp = {'qemu-desktop-images-092', 'HarmonyMac-reference-816', 'permissive-868', 'run-direct-observe-868.py', 'run-direct-observe-867.py', 'run-permissive-825.py', 'run-permissive-818.py', 'arm-local-751-config.json', 'arm-system-751-remote.py', 'inspect-direct-observe-869.py', 'inspect-permissive-819.py', 'direct-observe-864', 'permissive-kernel-823'}
unrelated = {'ego-venus-iova-offline-hlx92z3d','gaokun-packaging-audit','linux-gaokun3-aur-audit','linux-gaokun-audit-7463df37','__pycache__'}
known_plain = {'harmony-arm64-vm-smoke','harmony-samgr-audit','matebook-ego-iso-manifest-initial.json','matebook-loader-first-result.json','matebook-qemu-baseline-result.json','openharmony-token-6-audit','rebuild-ohos-private.py','run-matebook-binder-namespace.py','run_init_namespace_bundle.py','run_original_init_policy.py','wsl-not-matebook-inventory.json'}
temp_targets=[p for p in temp.iterdir() if p.name not in keep_temp|unrelated and (re.search(r'\d{3}',p.name) or p.name in known_plain)]
project_targets=[project/n for n in ['archive','configs','docs','HarmonyOS-7.0.0','probes','profiles','tests','tools'] if (project/n).exists()]
report_keep={'direct-observe-build-864.json','permissive-kernel-link-823.json','hdc-812.json','permissive-868.json','direct-observe-evidence-869.json'}
project_targets += [p for p in (project/'reports').iterdir() if p.name not in report_keep]
def writable_retry(func,path,exc):
    if not isinstance(exc,PermissionError):raise exc
    os.chmod(path,stat.S_IWRITE)
    func(path)
def remove_explicit(paths):
    deleted=[]
    for p in paths:
        assert p.parent in [temp,project,project/'reports']
        if p.is_symlink() or not p.is_dir():p.unlink()
        else:shutil.rmtree(p,onexc=writable_retry)
        deleted.append(str(p))
    return deleted
results['local_deleted']=remove_explicit(temp_targets+project_targets)
# Only the Image in the old kernel output is a live wrapper dependency.
for p in (temp/'permissive-kernel-823').iterdir():
    if p.name=='Image':continue
    if p.is_symlink() or not p.is_dir():p.unlink()
    else:shutil.rmtree(p,onexc=writable_retry)
results['local_free_after']={str(p):shutil.disk_usage(p).free for p in [project,temp]}
results['local_remaining_temp']=[p.name for p in temp.iterdir()]
with report.open('x') as f:json.dump(results,f,indent=2)
print(json.dumps({k:results[k] for k in ['matebook','wsl','local_free_after']},indent=2))
print('Deleted local entries:',len(results['local_deleted']))
