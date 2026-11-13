"""Run unchanged 020 ABI probe with the original-SDK Binder/SELinux configuration profile."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('run-baremetal-selinux-qemu-020.py')))['payload']
changes={
    "work=root/'baremetal-selinux-qemu-020';local=Path('/mnt/d/lab/HarmonyOSForMatebookego/reports/baremetal-selinux-qemu-020')":
        "work=root/'baremetal-selinux-qemu-021';local=Path('/mnt/d/lab/HarmonyOSForMatebookego/reports/baremetal-selinux-qemu-021')",
    "candidate=root/'baremetal-identity-candidate-002'":"candidate=root/'baremetal-identity-profile-003'",
    "previous=root/'baremetal-identity-qemu-002';assert json.loads((previous/'result.json').read_text())['runtime_verified']":
        "profile=json.loads((candidate/'result.json').read_text());assert profile['compiled'] and profile['parent_config_unchanged'] and profile['source_critical_unchanged'] and profile['driver_unchanged']",
    "build=previous/'out';kernel=build/'arch/arm64/boot/Image';expected='130f30abc9c9fc8faf1fb84bec268a1cde10fabdc3c93839250f347924f27bad'":
        "build=candidate/'test-out';kernel=build/'arch/arm64/boot/Image';expected=profile['test_kernel']['sha256'];assert sha(build/'.config')==profile['test_config_sha256'] and sha(candidate/'out/.config')==profile['native_config_sha256']",
    "critical=json.loads((candidate/'result.json').read_text())['patched_critical_hashes']":
        "critical=json.loads((root/'baremetal-identity-candidate-002/result.json').read_text())['patched_critical_hashes']",
}
for old,new in changes.items():
    assert payload.count(old)==1,old
    payload=payload.replace(old,new)
anchor=" report['actual_identity_devices_under_enforcing_policy_verified']=True"
assert payload.count(anchor)==1
payload=payload.replace(anchor," report['native_profile_config_changes']=profile['config_changes']\n"+anchor)
compile(payload,'selinux-021-qemu','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=160)
    raise SystemExit(r.returncode)
