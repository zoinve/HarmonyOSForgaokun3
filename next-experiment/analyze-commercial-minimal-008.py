"""Read-only evidence analysis; preserve the user's manual-recovery correction."""
from pathlib import Path
import hashlib, json, re

root=Path(__file__).resolve().parent.parent/'reports/commercial61-native-008'
raw=root/'runtime-evidence/raw'
manifest=json.loads((root/'runtime-evidence/retrieval-manifest.json').read_text())
for name, expected in manifest['files'].items():
    blob=(raw/name).read_bytes()
    assert len(blob)==expected['bytes']
    assert hashlib.sha256(blob).hexdigest()==expected['sha256'],name
phase=max(raw.glob('phase-*.log'),key=lambda p:int(p.stem.split('-')[1]))
s=phase.read_text(errors='replace')
h=(raw/'interactive-hilog030.log').read_text(errors='replace')
f=(raw/'interactive-faults030.log').read_text(errors='replace')
result={
    'run':manifest['run'], 'files_rehashed':len(manifest['files']),
    'user_report':'卡死手动重启', 'recovery':'user_manual_reboot',
    'automatic_return_verified':False,
    'runner_returned_means_ubuntu_online_only':True,
    'latest_phase':phase.name,
    'target_timeout_observed':'\nCOMMERCIAL008 target_timeout=1\n' in s,
    'target_exit_status9_observed':'COMMERCIAL008_TARGET_EXIT pid=303 status=9' in s,
    'target_end_observed':'NATIVE_ORIGINAL_END' in s,
    'kernel_deadlock_established':False,
    'profile_discovery_path_observed':'/usr/system/profile' in f and 'CFG_PATH' in f,
    'original_installs_service_started':'installd OnStart' in h,
    'sa511_not_supported_count':len(re.findall(r'LoadSystemAbility SA:511\b[^\n]*not supported',h)),
    'sceneboard_install_success':'finish install com.ohos.sceneboard resultCode: 0' in h,
    'sceneboard_process_observed':bool(re.search(r'COMMERCIAL001_PROCESS[^\n]*cmd=[^\n]*(?:sceneboard|SceneBoard)',s)),
    'guest_data_enospc_count':len(re.findall(r'errno[:= ]+28\b',h)),
    'sqlite_full_sys28_count':h.count('Error[13], sys[28]'),
    'mali_driver_failure_persists':'Failed creating base context during opening of kernel driver.' in f,
    'desktop_verified':False, 'sdk_userland_used':False,
    'original_partition_replayed':False,
}
evidence=[]
for text in [s,h,f]:
    for line in text.splitlines():
        if any(x in line for x in ['COMMERCIAL008 target_timeout=1','COMMERCIAL008_TARGET_EXIT',
            'NATIVE_ORIGINAL_END','installd OnStart','finish install com.ohos.sceneboard resultCode: 0',
            'CreateBundleDir:128 create bundle dir','Failed creating base context during opening of kernel driver.']):
            if line not in evidence:evidence.append(line)
assert result['files_rehashed']==59
assert result['target_timeout_observed'] and result['original_installs_service_started']
assert result['sceneboard_install_success'] and result['guest_data_enospc_count']>0
(root/'manual-recovery-analysis.json').open('x',encoding='utf-8').write(json.dumps(result,ensure_ascii=False,indent=2))
(root/'manual-recovery-evidence.txt').open('x',encoding='utf-8').write('\n'.join(evidence)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
