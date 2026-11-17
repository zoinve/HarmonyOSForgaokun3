"""Read source and original image inventories; never issue a secure-world call."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parent.parent
KERNEL = Path('/home/zoinve/ego-kernel-diag-20261101/linux')
IMAGES = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092')


def digest(body):
    return hashlib.sha256(body).hexdigest()


def directory(image, path):
    process = subprocess.run(['debugfs', '-R', 'ls -p '+path, str(image)], capture_output=True, check=True)
    rows = []
    for line in process.stdout.decode(errors='replace').splitlines():
        fields = line.split('/')
        if len(fields) < 7 or not fields[1].isdigit() or fields[5] in ('.', '..', ''):
            continue
        rows.append(dict(name=fields[5], mode=fields[2], bytes=int(fields[6]) if fields[6].isdigit() else None))
    return rows


if __name__ == '__main__':
    out = ROOT/'reports/native-tee-compatibility-096-r2.json'
    assert not out.exists()
    refs = [
        ('adaptations', ROOT/'references/L410-HarmonyOS-Adaptations', '205ad35e322f50993783f6bae48641abfa0dcf62'),
        ('linux_compatibility', ROOT/'references/L410-Linux-Compatibility-Platform', 'd95fbcecbf780e4086aa90f0c7ad052577121f11'),
        ('harmonymac', Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816'), 'f23a5d73f86ef0e45d3e7ac879a0605049a3c9ad'),
    ]
    references = []
    for name, repo, expected in refs:
        commit = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
        assert commit == expected
        names = subprocess.check_output(['git', '-C', str(repo), 'ls-tree', '-r', '--name-only', 'HEAD'], text=True).splitlines()
        references.append(dict(name=name, commit=commit, tee_named_source_paths=[n for n in names if re.search(r'tee|tzdriver|qsee', n, re.I)]))
    bridge_path = refs[0][1]/'fingerprint/tee_ioctl_abi_bridge_v1.c'
    bridge = bridge_path.read_bytes()
    assert b'NEW_CTX_SIZE 0xa0UL' in bridge and b'OLD_CTX_SIZE 0xb0UL' in bridge
    assert b'raw_ioctl(fd, old_request, &old_ctx)' in bridge
    qsee_path = KERNEL/'drivers/firmware/qcom/qcom_qseecom.c'
    qsee = qsee_path.read_bytes()
    array = re.search(rb'qcom_qseecom_apps\[\]\s*=\s*\{(.*?)\n\};', qsee, re.S)
    assert array
    apps = [s.decode() for s in re.findall(rb'\{\s*"([^"]+)"', array[1])]
    assert apps == ['qcom.tz.uefisecapp']
    inventories = []
    for image_name, root in [('p109-vendor.kr990-ext4-v1.img', '/'),
                             ('p111-system.kr990-ext4-v1.img', '/system')]:
        image = IMAGES/image_name
        pending = [(root, 0)]
        checked = []
        relevant = []
        while pending:
            path, depth = pending.pop(0)
            rows = directory(image, path)
            if depth == 0:
                assert rows, ('image root has no readable entries', image_name, path)
            checked.append(dict(path=path, entries=len(rows)))
            assert len(checked) <= 180, 'bounded inventory directory limit'
            for row in rows:
                name = path.rstrip('/')+'/'+row['name']
                if re.search(r'teec|cadaemon|tzdriver|tc_ns|itrustee|\.sec$|device.?cert|dcm', name, re.I):
                    relevant.append(dict(path=name, **row))
                if row['mode'].startswith('04') and depth < 3:
                    if depth == 0 and row['name'] in ('bin', 'lib64', 'etc', 'firmware'):
                        pending.append((name, depth+1))
                    elif depth > 0 and re.search(r'/bin|/lib64|tee|tui|/etc/(?:init|tee|trusted|security)|/firmware', name, re.I):
                        pending.append((name, depth+1))
        inventories.append(dict(image=image_name, directories=checked, relevant_metadata=relevant,
                                inventory_bounded_not_exhaustive=True, file_contents_exported=False))
    record = dict(references=references,
        preceding_audit='native-tee-compatibility-096.json',
        preceding_scope_error='vendor image uses / as its filesystem root, not /vendor; zero prior matches cannot prove absence',
        l410_bridge=dict(path=str(bridge_path.relative_to(ROOT)), sha256=digest(bridge),
                        source_context_bytes=160, target_context_bytes=176,
                        delegates_to_existing_driver_ioctl=True, provides_kernel_or_secure_firmware=False),
        kernel=dict(commit=subprocess.check_output(['git','-C',str(KERNEL),'rev-parse','HEAD'],text=True).strip(),
                    source_path=str(qsee_path), source_sha256=digest(qsee), statically_registered_apps=apps,
                    original_tc_ns_device_compatibility_not_established=True),
        original_image_inventories=inventories, target_booted=False,
        original_image_written=False, secure_firmware_called=False,
        security_storage_read=False, device_or_identity_replacement_created=False)
    out.open('x').write(json.dumps(record, indent=2))
    print(json.dumps(dict(kernel_apps=apps, references=[r['name'] for r in references],
        original_metadata_matches={i['image']:len(i['relevant_metadata']) for i in inventories},
        target_booted=False, secure_firmware_called=False), indent=2))
