"""Fresh private RAM-backed ext4 only; original SDK drives remain hardware read-only."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-036.py')))['payload']
for old,new in [('baremetal-sdk-original-init-qemu-036','baremetal-sdk-original-init-qemu-037'),
                ('baremetal-sdk-original-init-036','baremetal-sdk-original-init-037'),('ORIGINAL_INIT036_','ORIGINAL_INIT037_')]:
    assert old in payload;payload=payload.replace(old,new)
anchor='report=dict(bounded_observation_complete=False'
assert payload.count(anchor)==1
payload=payload.replace(anchor,'''import os,shutil,tempfile
assert shutil.which('mkfs.ext4') and shutil.disk_usage('/dev/shm').free > 768*1024*1024
work.chmod(0o700)
scratch_fd,scratch_name=tempfile.mkstemp(prefix='harmony-sdk-qemu037-',suffix='.ext4',dir='/dev/shm')
scratch=Path(scratch_name)
os.fchmod(scratch_fd,0o600);os.ftruncate(scratch_fd,512*1024*1024);os.close(scratch_fd)
mkfs=subprocess.run(['mkfs.ext4','-q','-F','-m','0','-L','sdk-volatile-data',
 '-E','lazy_itable_init=0,lazy_journal_init=0',str(scratch)],capture_output=True,text=True,timeout=60)
(work/'scratch-mkfs.stdout').write_text(mkfs.stdout);(work/'scratch-mkfs.stderr').write_text(mkfs.stderr)
mkfs.check_returncode()
scratch_before=sha(scratch)
command+=['-drive','file='+str(scratch)+',if=none,id=sdkdata,format=raw',
 '-device','virtio-blk-device,drive=sdkdata,serial=sdk-testdata']
'''+anchor)
# Record scratch metadata in the same report without changing readiness criteria.
anchor="start=time.monotonic();serial=work/'serial.log'"
assert payload.count(anchor)==1
payload=payload.replace(anchor,"report['scratch_data']=dict(freshly_formatted=True,ram_backed=True,original_userdata_attached=False,bytes=512*1024*1024,before_sha256=scratch_before)\n"+anchor)
anchor=" (work/'result.json').write_text(json.dumps(report,indent=2));"
assert payload.count(anchor)==1
payload=payload.replace(anchor,''' retained=work/'scratch-data.ext4'
 assert not retained.exists()
 copied=subprocess.run(['cp','--sparse=always','--',str(scratch),str(retained)],capture_output=True,text=True,timeout=60)
 copied.check_returncode();retained.chmod(0o600)
 after=sha(scratch);assert retained.stat().st_size==512*1024*1024 and sha(retained)==after
 report['scratch_data'].update(after_sha256=after,retained_path=str(retained),retained_copy_verified=True)
 assert scratch.parent==Path('/dev/shm') and scratch.name.startswith('harmony-sdk-qemu037-')
 scratch.unlink()  # Only this run's mkstemp file; verified private evidence is retained.
'''+anchor)
compile(payload,'original-init-037-qemu','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=360)
    raise SystemExit(r.returncode)
