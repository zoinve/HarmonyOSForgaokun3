"""Fresh single-factor archive: change only five verified Mesa libraries versus 010."""
from pathlib import Path
import runpy
import subprocess

parent=runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-diagnostic-init-010.py')))
source=parent['source']
payload=parent['payload'].replace('baremetal-diagnostic-init-010','baremetal-diagnostic-init-011')
assert payload.count('baremetal-freedreno-fence-package-001')==2
payload=payload.replace('baremetal-freedreno-fence-package-001','baremetal-freedreno-fence-package-002')
start=payload.index("r=subprocess.run(['aarch64-linux-gnu-gcc','-static','-O2','-Wall','-Wextra','-Werror',str(work/launcher_source.name)")
end=payload.index('\nadditions=[]',start)
payload=payload[:start]+'''import shutil
old010=root/'baremetal-diagnostic-init-010'
old_result=json.loads((old010/'result.json').read_text())
assert sha(old010/'mesa-launcher')==old_result['launcher_sha256']
assert sha(launcher_source)==old_result['launcher_source_sha256']
gpu_verified=json.loads((project/'reports/baremetal-freedreno-fence-run-002/independent-verification.json').read_text())
assert gpu_verified and manifest['probe_reused_unchanged']
shutil.copyfile(old010/'mesa-launcher',work/'mesa-launcher')
(local/'launcher-compile.stdout').write_text('REUSED exact verified 010 launcher; no compilation\\n')
(local/'launcher-compile.stderr').write_text('')
'''+payload[end:]
anchor="(work/'result.json').write_text(json.dumps(d,indent=2)+'\\n');"
assert payload.count(anchor)==1
comparison=r'''
def contents_of_archive(path):
    data=gzip.decompress(path.read_bytes());pos=0;entries={}
    while True:
        header=data[pos:pos+110];assert header[:6]==b'070701'
        values=[int(header[6+i*8:14+i*8],16) for i in range(13)]
        size=values[6];namesize=values[11]
        name=data[pos+110:pos+109+namesize].decode()
        body=(pos+110+namesize+3)&~3;pos=(body+size+3)&~3
        if name=='TRAILER!!!':break
        assert name not in entries
        entries[name]=(values[1],values[2],values[3],data[body:body+size])
    return entries
old_entries=contents_of_archive(old010/'diagnostic-init.cpio.gz')
new_entries=contents_of_archive(work/'diagnostic-init.cpio.gz')
assert old_entries.keys()==new_entries.keys()
changed=sorted(name for name in old_entries if old_entries[name]!=new_entries[name])
expected_changes=sorted('opt/native-mesa-001/lib/'+name for name in
 ['libEGL.so.1','libGLESv2.so.2','libgbm.so.1','libgallium-25.0.1.so','gbm/dri_gbm.so'])
assert changed==expected_changes,changed
assert sha(old010/'diagnostic-init.cpio.gz')==old_result['archive_sha256']
d.update(compared_with_candidate010=True,changed_archive_entries=changed,
         only_five_mesa_libraries_changed=True,launcher_reused_unchanged=True,
         native_gpu_execution_verified=False)
'''
payload=payload.replace(anchor,comparison+'\n'+anchor)
compile(payload,'prepare-native-mesa-011','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(r.returncode)
