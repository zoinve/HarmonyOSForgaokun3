"""Independent full archive audit; no installation, device access or target execution."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('verify-native-presentation-package-043.py')))['payload']
payload = payload.replace('native-original-graphics-boot-043', 'native-original-graphics-boot-044')
payload = payload.replace('native-presentation-package-043-independent', 'native-presentation-package-044-independent')
payload = payload.replace("old=root/'native-original-graphics-boot-041'", "old=root/'native-original-graphics-boot-043'")
old = "assert (work/'bootstrap.c').read_bytes()==(old/'bootstrap.c').read_bytes()"
assert payload.count(old) == 1
payload = payload.replace(old, """builder=runpy.run_path(str(project/'next-experiment/build-native-original-graphics-boot-044.py'))
assert builder['restore_inner']((work/'bootstrap.c').read_text())==(old/'bootstrap.c').read_text()
early=Path('/home/zoinve/harmony-virgl-883/baremetal-sdk-init-bootstrap-002/init_early.elf')
assert sha(early)=='9b475fa2588d4a7f46995de26d61689ce1bb8f1b7ce2c4588fac00c244c94824'""")
payload = payload.replace(".replace('native-interactive-041-%s','native-interactive-043-%s').replace('NATIVE_UNATTENDED041','NATIVE_UNATTENDED043')",
                          ".replace('native-interactive-043-%s','native-interactive-044-%s').replace('NATIVE_UNATTENDED043','NATIVE_UNATTENDED044')")
payload = payload.replace("kept={'init',vdi}", "kept={'init',vdi,'native-target/bootstrap'}")
payload = payload.replace("{'init',vdi,scratch}==set(claimed['changed_vs041'])", "{'init','native-target/bootstrap',scratch}==set(claimed['changed_vs043'])")
payload = payload.replace("assert after['init']['sha256']==sha(work/'init')", "assert after['init']['sha256']==sha(work/'init')\nassert after['native-target/bootstrap']['sha256']==sha(work/'bootstrap')")
anchor = "older=project/'reports/baremetal-native-trial-012-collected'"
assert payload.count(anchor) == 1
payload = payload.replace(anchor, """current=project/'reports/native-original-graphics-boot-043/runtime-evidence'
current_manifest=json.loads((current/'retrieval-manifest.json').read_text())
assert len(current_manifest['files'])==71
for name,row in current_manifest['files'].items():
 assert Path(name).name==name
 p=current/'raw'/name
 assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
""" + anchor)
payload = payload.replace('changed_vs041=changes', 'changed_vs043=changes').replace('unchanged_vs041=', 'unchanged_vs043=')
payload = payload.replace('bootstrap_source_unchanged=True', 'bootstrap_source_changes_only_original_mnt_restore=True')
payload = payload.replace('existing_native041_raw_files_verified=71,', 'existing_native041_raw_files_verified=71,existing_native043_raw_files_verified=71,')
compile(payload, 'independent-native-original-mnt-044', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=300).returncode)
