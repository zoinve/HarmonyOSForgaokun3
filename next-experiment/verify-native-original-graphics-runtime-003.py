"""Read-only outcome analysis; distinguish root repair from service/desktop success."""
from pathlib import Path
import hashlib
import json
import re

def verify(root, data_bytes=536870912):
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
    assert 'NATIVE_ROOT_NAMESPACE003 rooted=1 chroot_fallback=0' in text
    states=re.findall(r'NATIVE_DIAG002_STAT sample=(\d+) path=/proc/1/root/data rc=(-?\d+) errno=(\d+)',text)
    later=[row for row in states if int(row[0])>0]
    # Root repair is proven only after original init has run, not at sample 0.
    root_stable=bool(later) and all(rc=='0' for sample,rc,error in later)
    modes=re.findall(r'NATIVE_GRAPHICS001_SELINUX sample=(\d+) enforce=(.)',text)
    assert modes and all(mode=='0' for sample,mode in modes)
    for i,size in enumerate([3670016000,104857600,1048576000]):
        assert f'NATIVE_LOOP index={i} readonly=1 bytes={size} ram_data=0' in text
    assert f'NATIVE_LOOP index=3 readonly=0 bytes={data_bytes} ram_data=1' in text
    assert d['screen_off_timer']=='active' and d['ubuntu_lsm']=='capability,landlock'
    assert d['original_images_verified_unchanged']==3
    assert 'Default Entry: 8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf' in d['boot_status']
    assert 'OneShot Entry:' not in d['boot_status']
    return dict(raw_snapshots_verified=len(d['logs']),root_namespace_created=True,
        init_root_stable_verified=root_stable,init_root_data_states=states,
        target_selinux_permissive_samples=len(modes),
        early_policy_load_audit_retained=('lsm=selinux res=1' in text),
        ubuntu_return_verified=True,original_images_verified_unchanged=3,
        efi_files_verified_unchanged=d['efi_files_verified_unchanged'],
        service_process_samples=len(re.findall('NATIVE_GRAPHICS001_PROCESS ',text)),
        service_library_samples=len(re.findall('NATIVE_GRAPHICS001_MAP ',text)),
        desktop_verified=False)

if __name__=='__main__':
    print(json.dumps(verify(Path(__file__).resolve().parent.parent/'reports/native-original-graphics-boot-003'),indent=2))
