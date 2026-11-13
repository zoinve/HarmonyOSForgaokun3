"""Independent raw-evidence verification for diagnostic trial 002 (read only)."""
from pathlib import Path
import hashlib
import json
import re

def verify(root):
    d=json.loads((root/'runtime-result.json').read_text())
    before=json.loads((root/'boot-attempt.json').read_text())
    assert d['boot_id_after']!=before['boot_id_before']
    for row in d['logs']:
        p=root/'native-logs'/row['name']
        assert p.parent==root/'native-logs' and p.is_file() and not p.is_symlink()
        assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],row['name']
    text=(root/'native-logs'/d['logs'][-1]['name']).read_bytes().decode(errors='replace')
    assert 'release=7.1.0-rc3-gaokun3-el2 ' in text
    assert 'NATIVE_DIAGNOSTIC_END' in text and 'NATIVE_ORIGINAL_END' in text
    assert re.search(r'NATIVE_ORIGINAL_START real_pid=[1-9]\d* ',text)
    # Verbose init logs rolled the early load audit out of the kernel ring.
    # Labelled AVC evidence proves policy is active, but is not the load audit.
    assert 'scontext=u:r:kernel:s0 tcontext=u:object_r:hilog_exec:s0' in text
    assert 'permissive=1' in text
    assert re.findall(r'NATIVE_GRAPHICS001_SELINUX sample=(\d+) enforce=(.)',text)==[(str(i),'0') for i in range(12)]
    for path in ['/proc/1/mountinfo','/proc/1/status','/proc/1/wchan']:
        assert re.search(r'NATIVE_DIAG002_FILE sample=1 path='+re.escape(path)+r' bytes=[1-9]\d* errno=0',text),path
    assert 'NATIVE_DIAG002_STAT sample=1 path=/data ' in text
    assert 'NATIVE_DIAG002_PROCESS sample=1 pid=1 ' in text
    assert 'NATIVE_DIAG002_HOST_PROCESS ' in text
    assert 'NATIVE_DIAG002_PRINTK rc=3 ' in text
    for i,size in enumerate([3670016000,104857600,1048576000]):
        assert f'NATIVE_LOOP index={i} readonly=1 bytes={size} ram_data=0' in text
    assert 'NATIVE_LOOP index=3 readonly=0 bytes=536870912 ram_data=1' in text
    assert d['screen_off_timer']=='active' and d['ubuntu_lsm']=='capability,landlock'
    assert d['original_images_verified_unchanged']==3
    assert 'Default Entry: 8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf' in d['boot_status']
    assert 'OneShot Entry:' not in d['boot_status']
    return dict(raw_snapshots_verified=len(d['logs']),diagnostic_coverage_verified=True,
        selinux_policy_active_permissive=True,early_policy_load_audit_retained=('lsm=selinux res=1' in text),
        init_root_escaped=bool(re.search(r'NATIVE_DIAG002_STAT sample=1 path=/proc/1/root/data rc=-1 errno=2 ',text)),
        ubuntu_return_verified=True,
        original_images_verified_unchanged=3,efi_files_verified_unchanged=d['efi_files_verified_unchanged'],
        service_process_samples=len(re.findall('NATIVE_GRAPHICS001_PROCESS ',text)),
        service_library_samples=len(re.findall('NATIVE_GRAPHICS001_MAP ',text)),desktop_verified=False)

if __name__=='__main__':
    print(json.dumps(verify(Path(__file__).resolve().parent.parent/'reports/native-original-graphics-boot-002'),indent=2))
