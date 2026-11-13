"""Re-read real archives and immutable originals; no deployment or target execution."""
import subprocess

payload = r'''
from pathlib import Path,PurePosixPath
import hashlib,json,gzip,runpy
project=Path('/mnt/d/lab/HarmonyOSForMatebookego')
root=Path('/home/zoinve/harmony-virgl-883')
work=root/'native-original-graphics-boot-043'
local=project/'reports/native-original-graphics-boot-043'
report=project/'reports/native-presentation-package-043-independent'
assert not report.exists()
report.mkdir()
def sha(path):
 with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def load_pair(name):
 assert sha(work/name)==sha(local/name),name
 return json.loads((work/name).read_text())
candidate=load_pair('result.json')
claimed=load_pair('presentation-overlay-audit.json')
assert not candidate['native_boot_attempted'] and not candidate['automatic_input_injection']
assert candidate['original_images_readonly'] and candidate['original_service_credentials_unmodified']
assert candidate['outer_deadline_seconds']==420 and candidate['original_service_observation_seconds']==240
candidate_files={}
for row in candidate['artifacts']:
 path=work/row['name']
 assert path.is_file() and not path.is_symlink() and path.stat().st_size==row['bytes'] and sha(path)==row['sha256']
 candidate_files[row['name']]=row
old=root/'native-original-graphics-boot-041'
old_result=json.loads((old/'result.json').read_text())
old_guards={}
for row in old_result['artifacts']:
 path=old/row['name']
 assert path.stat().st_size==row['bytes'] and sha(path)==row['sha256']
 old_guards[str(path)]=row['sha256']
assert (work/'bootstrap.c').read_bytes()==(old/'bootstrap.c').read_bytes()
expected_outer=(old/'init.c').read_text().replace('native-interactive-041-%s','native-interactive-043-%s').replace('NATIVE_UNATTENDED041','NATIVE_UNATTENDED043')
assert (work/'init.c').read_text()==expected_outer
for name in ('linux','sc8280xp-huawei-gaokun3.dtb'):
 assert sha(work/name)==sha(old/name)
reader_path=project/'next-experiment/native-presentation-archive-043.py'
reader_hash=sha(reader_path)
scan=runpy.run_path(str(reader_path))['scan_cpio']
def index(path, keep):
 with gzip.open(path,'rb') as stream:return scan(stream,keep)
vdi='native-target/graphics-provider/libdisplay_composer_vdi_impl.z.so'
scratch='native-target/scratch-data.ext4'
kept={'init',vdi}
before,_=index(old/'initrd.img',set())
after,small=index(work/'initrd.img',kept)
assert before.keys()==after.keys()
changes=[]
for name in before:
 assert before[name]['metadata']==after[name]['metadata'],name
 if before[name]['sha256']!=after[name]['sha256']:changes.append(name)
assert set(changes)=={'init',vdi,scratch}==set(claimed['changed_vs041'])
assert after['init']['sha256']==sha(work/'init')
module=root/'native-presentation-043'
module_manifest=json.loads((module/'result.json').read_text())
assert sha(module/'result.json')=='42e3b335598148c0482ca821a26215cdd7dd35a3ae1e806bb2112a4a0c521d65'
assert after[vdi]['sha256']==module_manifest['files']['libdisplay_composer_vdi_impl.z.so']['sha256']==sha(module/'libdisplay_composer_vdi_impl.z.so')
for p,digest in module_manifest['guarded_inputs'].items():assert sha(p)==digest,p
base=root/'native-original-graphics-boot-032'
base_result=json.loads((base/'result.json').read_text())
base_row=next(r for r in base_result['artifacts'] if r['name']=='initrd.img')
assert sha(base/'initrd.img')==base_row['sha256']=='78049c130b3ab1dcd8f29d192b168bed3681d16a8aa9c298e6b548987e51f8ad'
baseline,_=index(base/'initrd.img',set())
assert baseline.keys()==after.keys()
for name in baseline:
 assert baseline[name]['metadata']==after[name]['metadata'],name
 if name not in kept|{scratch}:assert baseline[name]['sha256']==after[name]['sha256'],name
overlay=work/'return-overlay.img'
assert overlay.stat().st_size==claimed['overlay']['bytes'] and sha(overlay)==claimed['overlay']['sha256']
actual_overlay,overlay_small=index(overlay,kept)
assert set(actual_overlay)==kept and overlay_small==small
for name in kept:assert actual_overlay[name]==after[name]
assert claimed['scratch_reused_from_base032'] and claimed['base032_scratch']==baseline[scratch]
# Independent complete original-image hashes, not executable probes.
image_hashes={
 'system.img':'19922349cf9550aea47c241efa42bfaae00060028e5db5c2445fc3796ba324d3',
 'vendor.img':'4e0c24992070e10cb35277faf8fda1e27241d455c677d58289a6bf0d75a0f8f7',
 'sys_prod.img':'41fa2bbc6862262cf1b87149b2218e019d385abc03599abc5f04155e11623b78'}
for name,digest in image_hashes.items():assert sha(Path('/mnt/d/Download/pc_all_arm')/name)==digest,name
prior=project/'reports/native-original-graphics-boot-041/runtime-evidence'
retrieval=json.loads((prior/'retrieval-manifest.json').read_text())
assert len(retrieval['files'])==71
for name,row in retrieval['files'].items():
 assert Path(name).name==name
 path=prior/'raw'/name
 assert path.stat().st_size==row['bytes'] and sha(path)==row['sha256']
older=project/'reports/baremetal-native-trial-012-collected'
collection=json.loads((older/'collection.json').read_text())
assert len(collection['files'])==378
for row in collection['files']:
 relative=PurePosixPath(row['path'])
 assert not relative.is_absolute() and '..' not in relative.parts
 path=older/str(relative)
 assert path.stat().st_size==row['bytes'] and sha(path)==row['sha256']
for p,digest in old_guards.items():assert sha(p)==digest,p
assert sha(reader_path)==reader_hash
result=dict(candidate_files_verified=candidate_files,changed_vs041=changes,
 unchanged_vs041=len(before)-len(changes),archive_metadata_preserved=True,
 init_source_changes_only_run_labels=True,bootstrap_source_unchanged=True,
 kernel_and_dtb_retained=True,overlay_members_verified=sorted(kept),
 overlay_bytes=overlay.stat().st_size,overlay_sha256=sha(overlay),
 base032_scratch_reused=True,base032_scratch_sha256=baseline[scratch]['sha256'],
 original_images_independent_hashes=True,original_image_hashes=image_hashes,
 existing_native041_raw_files_verified=71,older_native012_raw_files_verified=378,
 trace_module_manifest_sha256=sha(module/'result.json'),reader_sha256=reader_hash,
 original_service_credentials_unmodified=True,original_images_readonly=True,
 automatic_input_injection=False,target_code_executed=False,device_accessed=False,
 installed=False,native_boot_attempted=False,runtime_verified=False,stable_120fps_verified=False)
with (report/'result.json').open('x') as f:json.dump(result,f,indent=2)
print(json.dumps({k:v for k,v in result.items() if k!='candidate_files_verified'},indent=2))
'''

if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=300).returncode)
