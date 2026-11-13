"""Verify collected immutable evidence, not the candidate's own success labels."""
from pathlib import Path
import hashlib
import json
import re

BASE=Path(__file__).resolve().parent.parent

def verify(root):
    result=json.loads((root/'runtime-result.json').read_text())
    attempt=json.loads((root/'boot-attempt.json').read_text())
    assert result['boot_id_after']!=attempt['boot_id_before']
    rows=result['logs'];assert len(rows)==49
    for row in rows:
        data=(root/'native-logs'/row['name']).read_bytes()
        assert hashlib.sha256(data).hexdigest()==row['sha256'],row['name']
    text=(root/'native-logs'/rows[-1]['name']).read_bytes().decode('utf-8','replace')
    assert 'release=7.1.0-rc3-gaokun3-el2 ' in text
    assert 'NATIVE_DIAGNOSTIC_END' in text and 'NATIVE_ORIGINAL_END' in text
    assert 'NATIVE_ORIGINAL_START real_pid=305' in text
    assert 'comm="init"' in text and 'scontext=u:r:init:s0' in text
    assert 'lsm=selinux res=1' in text
    samples=re.findall(r'NATIVE_GRAPHICS001_SELINUX sample=(\d+) enforce=(.)',text)
    assert samples==[(str(i),'0') for i in range(12)]
    for i,size in enumerate([3670016000,104857600,1048576000]):
        assert f'NATIVE_LOOP index={i} readonly=1 bytes={size} ram_data=0' in text
    assert 'NATIVE_LOOP index=3 readonly=0 bytes=536870912 ram_data=1' in text
    for name,minor in [('card0',0),('renderD128',128)]:
        assert f'path=/dev/dri/{name} dev=226:{minor}' in text
    assert 'NATIVE_GRAPHICS001_PROCESS ' not in text
    assert 'NATIVE_GRAPHICS001_MAP ' not in text
    assert 'Create file /data/.ro_test in /data failed![No such file or directory]' in text
    assert "cgroup: Unknown subsys name 'cpuset'" in text
    assert "cgroup: Unknown subsys name 'memory'" in text
    assert result['screen_off_timer']=='active' and result['ubuntu_lsm']=='capability,landlock'
    assert result['original_images_verified_unchanged']==3 and result['efi_files_verified_unchanged']==79
    return dict(raw_snapshots_verified=len(rows),native_original_init_executed=True,
        original_selinux_policy_loaded=True,permissive_samples=len(samples),real_drm_nodes_present=True,
        service_processes_observed=False,graphics_libraries_observed_in_services=False,
        data_path_error_observed=True,cgroup_v1_controller_mismatch_observed=True,
        service_startup_root_cause_established=False,desktop_verified=False,scanout_verified=False,
        ubuntu_return_verified=True,original_images_verified_unchanged=3,ubuntu_default_preserved=True,
        screen_off_timer_active=True,host_lsm_preserved=True)

if __name__=='__main__':
    print(json.dumps(verify(BASE/'reports/native-original-graphics-boot-001'),indent=2))
