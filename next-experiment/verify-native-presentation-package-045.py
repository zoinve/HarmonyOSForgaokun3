"""Independently audit capture-only bootstrap changes and all preserved payloads."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('verify-native-presentation-package-044.py')))['payload']
for old,new in [('native-original-graphics-boot-044','native-original-graphics-boot-045'),
                ('native-presentation-package-044-independent','native-presentation-package-045-independent'),
                ("old=root/'native-original-graphics-boot-043'","old=root/'native-original-graphics-boot-044'"),
                (".replace('native-interactive-043-%s','native-interactive-044-%s').replace('NATIVE_UNATTENDED043','NATIVE_UNATTENDED044')",
                 ".replace('native-interactive-044-%s','native-interactive-045-%s').replace('NATIVE_UNATTENDED044','NATIVE_UNATTENDED045')"),
                ('changed_vs043','changed_vs044'),
                ('bootstrap_source_changes_only_original_mnt_restore=True','bootstrap_source_changes_only_incremental_perf_capture=True')]:
    assert old in payload, old
    payload = payload.replace(old,new)
assert 'next-experiment/build-native-original-graphics-boot-045.py' in payload
assert 'unchanged_vs044' in payload
anchor = "current=project/'reports/native-original-graphics-boot-043/runtime-evidence'"
assert payload.count(anchor) == 1
payload = payload.replace(anchor, """recent=project/'reports/native-original-graphics-boot-044/runtime-evidence'
recent_manifest=json.loads((recent/'retrieval-manifest.json').read_text())
assert len(recent_manifest['files'])==71
for name,row in recent_manifest['files'].items():
 assert Path(name).name==name
 p=recent/'raw'/name
 assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
assert sha(project/'next-experiment/native-perf-capture-045.h')==claimed['capture_core_sha256']
assert claimed['bootstrap_source_changes_only_incremental_perf_capture'] is True
""" + anchor)
payload = payload.replace('existing_native043_raw_files_verified=71,',
                          'existing_native043_raw_files_verified=71,existing_native044_raw_files_verified=71,')
compile(payload,'independent-native-incremental-capture-045','exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=300).returncode)
