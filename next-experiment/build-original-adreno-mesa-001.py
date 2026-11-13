"""Build real OHOS Freedreno/MSM in a new directory; no device or installation."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('build-original-softpipe-001.py')))['payload']
payload = payload.replace('original-softpipe-001', 'original-adreno-mesa-001')
payload = payload.replace('-Dgallium-drivers=softpipe', '-Dgallium-drivers=freedreno')
payload = payload.replace("['softpipe']", "['freedreno']")
anchor = "args += ['-Dgallium-drivers=freedreno', '-Dlibdir=lib64/harmony-mesa']"
assert payload.count(anchor) == 1
payload = payload.replace(anchor, "args += ['-Dgallium-drivers=freedreno', '-Dlibdir=lib64/harmony-mesa', '-Dfreedreno-kmds=msm', '-Dallow-kcmp=enabled']")
anchor = 'before = {str(p): digest(p) for p in guards}'
assert payload.count(anchor) == 1
payload = payload.replace(anchor, """guards += [src/'src/freedreno/drm/msm/msm_device.c', src/'src/freedreno/drm/freedreno_device.c',
           root/'toolchain/ohos-cc', root/'toolchain/ohos-cxx']
""" + anchor)
anchor = "run(['ninja', '-C', str(work/'build'), '-j4'])"
assert payload.count(anchor) == 1
payload = payload.replace(anchor, """assert next(x['value'] for x in new_options if x['name']=='freedreno-kmds') == ['msm']
assert next(x['value'] for x in new_options if x['name']=='allow-kcmp') == 'enabled'
""" + anchor)
anchor = "    dynamic = subprocess.check_output(['llvm-readelf-19', '-dW', str(dest)], text=True)"
assert payload.count(anchor) == 1
payload = payload.replace(anchor, "    assert struct.unpack_from('<H', dest.read_bytes(), 18)[0] == 183\n" + anchor)
anchor = "'physical_board_test': False, 'installed': False, 'commands': commands"
assert payload.count(anchor) == 1
payload = payload.replace(anchor, "'physical_board_test': False, 'installed': False, 'device_accessed': False, 'kernel_modesetting_attempted': False, 'freedreno_kmds': ['msm'], 'allow_kcmp': 'enabled', 'commands': commands")
compile(payload, 'original-adreno-mesa-001-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=1200).returncode)
