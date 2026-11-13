"""Independently verify isolated GPU evidence, bundle hashes and read-only Ubuntu return state."""
from pathlib import Path
import hashlib
import json
import subprocess
import tarfile

base=Path(__file__).resolve().parent.parent
reports=base/'reports'
out=reports/'baremetal-freedreno-fence-run-002/independent-verification.json'
package=json.loads((reports/'baremetal-freedreno-fence-package-002/package.json').read_text())
prior=json.loads((reports/'baremetal-freedreno-fence-package-001/package.json').read_text())
run=json.loads((reports/'baremetal-freedreno-fence-run-002/result.json').read_text())
assert not out.exists()
archive=reports/'baremetal-freedreno-fence-package-002/bundle.tar.gz'
assert archive.stat().st_size==package['archive_bytes'] and hashlib.sha256(archive.read_bytes()).hexdigest()==package['archive_sha256']==run['package_sha256']
old={row['path']:row for row in prior['files']};new={row['path']:row for row in package['files']}
assert old.keys()==new.keys() and len(new)==9
changed={name for name in old if old[name]['sha256']!=new[name]['sha256']}
assert changed=={'lib/libEGL.so.1','lib/libGLESv2.so.2','lib/libgbm.so.1','lib/libgallium-25.0.1.so','lib/gbm/dri_gbm.so'},changed
assert new['probe']['sha256']=='3f124cf9743ab84e0b8732853743cbe6130235e3dcbdd17e1810fb4bf069468e'
with tarfile.open(archive) as tar:
    for name,row in new.items():
        data=tar.extractfile(name).read()
        assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
assert run['run']['returncode']==0 and run['gpu_pixel_test_passed'] and run['new_kernel_log']==''
assert not run['reboot_requested'] and not run['boot_entries_modified'] and not run['desktop_verified']
assert 'os_same_file_description' not in run['run']['stdout']+run['run']['stderr'] and not run['fd_identity_warning_present']
for marker in ['renderer=FD690','FENCE001_SYNC_FILE poll=1 revents=0x1','FENCE001_REIMPORT wait=0x30f6 status=0x30f2','FENCE001_PIXELS center=255,0,0,255 corner=0,0,255,255','FENCE001_MAPPED center_8_8=255,0,0,255 corner_0_8=0,0,255,255','FENCE001_PASS native_fence_and_dmabuf_coherence desktop_not_tested=1']:
    assert marker in run['run']['stdout'],marker
policy={'LoadState':'loaded','Transient':'yes','User':'zoinve','SupplementaryGroups':'render','DevicePolicy':'closed','DeviceAllow':'/dev/dri/renderD128 rw','CapabilityBoundingSet':'','NoNewPrivileges':'yes','ProtectSystem':'strict','ProtectHome':'yes','PrivateNetwork':'yes','PrivateTmp':'yes','RuntimeMaxUSec':'45s','MemoryMax':'536870912','TasksMax':'32','RestrictAddressFamilies':'AF_UNIX'}
for kind in ['effective_service_properties_before_probe','sandbox_effective_policy']:
    for key,value in policy.items():assert run[kind][key]==value,(kind,key)
payload='expected='+repr(package)+'\nrecord='+repr(run)+'\n'+r'''
from pathlib import Path
import hashlib,json,runpy,subprocess,os
assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()==record['boot_id']
assert os.uname().release==record['kernel']=='7.1.0-rc3-gaokun3+'
assert 'harmony.diag=1' not in Path('/proc/cmdline').read_text().split()
root=Path(record['stage']);count=0
for row in expected['files']:
    p=root/row['path'];assert p.is_file() and not p.is_symlink()
    assert p.stat().st_size==row['bytes']
    with p.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==row['sha256']
    count+=1
assert (root/'lib/libc.so').is_symlink() and os.readlink(root/'lib/libc.so')=='ld-musl-aarch64.so.1'
def readonly(args,**kwargs):
    assert 'set-property' not in args,'verification must not turn the screen off itself'
    return subprocess.run(args,**kwargs)
rows=runpy.run_path('/usr/local/libexec/harmony-lab-screen-off-001.py')['run_once'](runner=readonly)
assert rows and all(row['state']=='off' and not row['changed'] for row in rows),rows
assert subprocess.check_output(['systemctl','is-active','harmony-lab-screen-off-001.timer'],text=True).strip()=='active'
v=Path('/sys/firmware/efi/efivars');guid='4a67b082-0a4c-41cf-b6c7-440b29bb8c4f'
assert (v/('LoaderEntryDefault-'+guid)).read_bytes()[4:].decode('utf-16-le').rstrip('\0')=='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
one=v/('LoaderEntryOneShot-'+guid);assert not one.exists() or not one.read_bytes()[4:].decode('utf-16-le').rstrip('\0')
assert not list(Path('/boot/efi/loader/entries').glob('harmony-native-diag-*'))
print(json.dumps(dict(remote_files_verified=count,boot_id_unchanged=True,screen_rows=rows,screen_state_changed_by_verifier=False,physical_screen_observed=False,ubuntu_default_unchanged=True,one_shot_absent=True,consumed_entries_absent=True)))
'''
if __name__=='__main__':
    r=subprocess.run(['ssh','-o','ConnectTimeout=3','matebook','sudo -n python3 -'],input=payload,text=True,capture_output=True,timeout=75)
    assert r.returncode==0,r.stderr
    result=json.loads(r.stdout)
    result.update(archive_sha256=package['archive_sha256'],all_nine_archive_and_remote_files_verified=True,only_five_mesa_libraries_changed=sorted(changed),same_probe_executable_reused=True,gpu_pixels_dmabuf_and_native_fence_verified=True,live_sandbox_policy_verified=True,fd_identity_warning_absent=True,kernel_is_ubuntu=True,new_native_kernel_run_verified=False,desktop_verified=False)
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
