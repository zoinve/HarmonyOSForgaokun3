"""Attach only the original SDK system image as read-only, with before/after digest guards."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('run-baremetal-selinux-qemu-024.py')))['payload']
changes={
    'baremetal-selinux-qemu-024':'baremetal-selinux-qemu-025',
    'baremetal-selinux-identity-023':'baremetal-sdk-system-read-025',
    'SELINUX023_':'SELINUX025_',
    "build=candidate/'test-out';kernel=build/'arch/arm64/boot/Image';expected=profile['test_kernel']['sha256'];assert sha(build/'.config')==profile['test_config_sha256'] and sha(candidate/'out/.config')==profile['native_config_sha256']":
        "storage=json.loads((root/'baremetal-sdk-storage-test-004/result.json').read_text());assert storage['compiled'] and storage['test_only'];build=root/'baremetal-sdk-storage-test-004/out';kernel=build/'arch/arm64/boot/Image';expected=storage['test_kernel']['sha256'];assert sha(build/'.config')==storage['test_config_sha256'] and sha(candidate/'out/.config')==profile['native_config_sha256']",
    "def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()":
        "def sha(p):\n with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()",
}
for old,new in changes.items():
    assert old in payload,old
    payload=payload.replace(old,new)
anchor="report=dict(runtime_verified=False"
assert payload.count(anchor)==1
payload=payload.replace(anchor,"""image=Path('/mnt/d/Download/pc_all_arm/system.img');image_digest=sha(image);image_bytes=image.stat().st_size
command+=['-drive','file='+str(image)+',if=none,id=sdk_system,format=raw,readonly=on','-device','virtio-blk-device,drive=sdk_system']
"""+anchor)
payload=payload.replace('storage_devices_attached=False','storage_devices_attached=True,original_sdk_image_readonly=True')
anchor=" report['selinux_explicitly_added_to_baseline_lsm']=True;"
assert payload.count(anchor)==1
payload=payload.replace(anchor," assert 'SELINUX025_STORAGE_PASS readonly_block=1 readonly_noexec_noload_mount=1 original_samgr_label=1 original_elf_read=1 services_not_tested=1' in log\n report['original_sdk_readonly_filesystem_verified']=True\n"+anchor)
anchor=" report.update(elapsed_seconds="
assert payload.count(anchor)==1
payload=payload.replace(anchor," report['original_image_unchanged']=sha(image)==image_digest and image.stat().st_size==image_bytes\n report['original_image_sha256']=image_digest\n"+anchor)
anchor="print(json.dumps(report,indent=2),flush=True)"
assert payload.count(anchor)==1
payload=payload.replace(anchor,anchor+"\n assert report['original_image_unchanged'], 'Original image preservation failed; numbered result retained'")
compile(payload,'sdk-system-read-025-qemu','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=240)
    raise SystemExit(r.returncode)
