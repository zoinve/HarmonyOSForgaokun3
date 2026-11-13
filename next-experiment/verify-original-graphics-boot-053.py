"""Independent immutable virtual-graphics evidence, not desktop readiness."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

BASE = Path(__file__).resolve().parents[1]


def verify_mode_samples(raw, prefix):
    modes = re.findall(prefix + rb'SELINUX sample=(\d+) enforce=(\d)', raw)
    assert 16 <= len(modes) <= 24 and {v for _, v in modes} == {b'0'}
    assert [int(i) for i, _ in modes] == list(range(len(modes)))
    return len(modes)


def verify(number='053', tag='050', egl=False):
    out = BASE / ('reports/original-graphics-boot-' + number + '-independent.json')
    assert not out.exists()
    folder = BASE / ('reports/baremetal-sdk-original-init-qemu-' + number)
    result = json.loads((folder / 'result.json').read_text())
    raw = (folder / 'serial.log').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == result['serial_sha256']
    assert len(raw) == result['serial_bytes']
    assert all(result[k] for k in ['original_images_unchanged', 'kernel_and_config_unchanged',
                                  'native_config_unchanged', 'source_critical_unchanged'])
    assert not result['helper_failure_observed']
    assert result['observation_timed_out'] and result['qemu_returncode'] is None
    command = result['command']
    assert 'virtio-mmio.force-legacy=false' in command and 'virtio-gpu-device' in command
    assert command[command.index('-display') + 1] == 'none'
    assert command[command.index('-nic') + 1] == 'none'
    assert command[command.index('-accel') + 1] == 'tcg,thread=multi'
    assert not any(x in command for x in ['-virtfs', '-fsdev', '-blockdev'])
    assert sum('format=raw,readonly=on' in x for x in command) == 3
    prefix = ('GRAPHICS' + tag + '_').encode()
    assert b'[drm] Initialized virtio_gpu' in raw
    assert b'driver=../../../../bus/virtio/drivers/virtio_gpu' in raw
    for node, dev in [('card0', '226:0'), ('renderD128', '226:128')]:
        assert prefix + ('DEVICE path=/dev/dri/%s dev=%s uid=0 gid=1003 mode=0660' % (node, dev)).encode() in raw
    assert prefix + b'PROVIDER original_init_services=1 service_credentials_unmodified=1 volatile_vendor_only=1 physical_gpu=0' in raw
    # The guest is terminated by a wall-clock bound, not by observer completion.
    # TCG plus audit/proc output can end the run before all 24 intended samples.
    mode_samples = verify_mode_samples(raw, prefix)
    identities = {}
    for name, uid in [('composer_host', 3036), ('allocator_host', 3041), ('render_service', 1003)]:
        pids = sorted({int(p) for p in re.findall(prefix + rb'PROCESS sample=\d+ pid=(\d+) cmd=[^\r\n]*' + name.encode(), raw)})
        assert pids, name
        for pid in pids:
            assert prefix + ('IDENTITY pid=%d Uid:\t' % pid).encode() + b'\t'.join([str(uid).encode()] * 4) in raw
            assert prefix + ('DOMAIN pid=%d value=u:r:%s:s0' % (pid, name)).encode() in raw
        identities[name] = dict(pids=pids, uid=uid, domain='u:r:' + name + ':s0')
    for name in ['libdisplay_composer_vdi_impl.z.so', 'libdisplay_buffer_vdi_impl.z.so']:
        assert re.search(prefix + rb'MAP pid=\d+ [^\r\n]*/vendor/lib64/' + name.encode(), raw)
    if egl:
        assert prefix + b'EGL original_nativewindow=1 platform_libcxx_replaced=0 private_mesa_ndk_runtime=1 service_credentials_unmodified=1 physical_gpu=0' in raw
    collected = BASE / 'reports/baremetal-native-trial-012-collected'
    prior = json.loads((collected / 'collection.json').read_text())['files']
    assert len(prior) == 378
    for row in prior:
        body = (collected / row['path']).read_bytes()
        assert len(body) == row['bytes'] and hashlib.sha256(body).hexdigest() == row['sha256']
    # Independently re-read every original image and the actual injected cpio bytes.
    script = '''from pathlib import Path
import hashlib,json,runpy
project=Path('/mnt/d/lab/HarmonyOSForMatebookego')
root=Path('/home/zoinve/harmony-virgl-883')
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
result=json.loads(%r)
for row in result['original_images'].values():
 p=Path(row['path']);assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
archive=root/('baremetal-sdk-original-init-qemu-'+%r)/'initramfs.cpio.gz'
assert sha(archive)==result['initrd_sha256']
entries=runpy.run_path(str(project/'next-experiment/build-composer-parser-001.py'))['unpack'](archive.read_bytes())
sources=[('original-graphics-provider-002','graphics-provider/')]
if %r:sources.append(('original-graphics-egl-002','graphics-egl/'))
count=0
for package,prefix in sources:
 manifest=json.loads((project/('reports/'+package+'/result.json')).read_text())
 for row in manifest['files']:
  body=entries[prefix+row['name']][1]
  assert len(body)==row['bytes'] and hashlib.sha256(body).hexdigest()==row['sha256']
  assert sha(Path(row['path']))==row['sha256']
  count+=1
kernel=Path(result['command'][result['command'].index('-kernel')+1])
assert sha(kernel)=='a75433f6f069d6607d3a34c461ae3723287d7ae67d45d72a68c7983f12a50136'
print(json.dumps(dict(original_images_independent_hashes=True,injected_provider_files_verified=count,initrd_independent_hash=True,kernel_independent_hash=True)))
''' % (json.dumps(result), number, egl)
    checked = subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=script,
                             text=True, capture_output=True, check=True, timeout=150)
    evidence = dict(serial_sha256=result['serial_sha256'], observed_mode='permissive',
                    mode_samples=mode_samples, original_process_identities=identities,
                    genuine_virtual_drm_bound=True, reference_vdis_mapped=True,
                    prior_native_raw_files_verified=len(prior),
                    foundation_critical_fault_observed=b'ProcessCriticalProcessFault serviceName is foundation' in raw,
                    guest_reboot_observed=b'reboot: Restarting system' in raw,
                    readiness_verified=False, desktop_verified=False, physical_board_test=False,
                    independent_artifacts=json.loads(checked.stdout))
    with out.open('x') as f:
        json.dump(evidence, f, indent=2)
    print(json.dumps(evidence, indent=2))


if __name__ == '__main__':
    verify()
