"""Verify unchanged original graph and genuine, hash-pinned guest ashmem loading."""
from pathlib import Path
import runpy

parent = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-073.py')))


def parse_state_records(raw):
    return parent['parse_state_records'](raw.replace(b'GRAPHICS074_STATE ', b'GRAPHICS073_STATE '))


source = parent['source']
assert source.count("number='073', tag='073'") == 1
source = source.replace("number='073', tag='073'", "number='074', tag='074'")
source = source.replace('GRAPHICS073_', 'GRAPHICS074_')
source = source.replace('next-experiment/verify-original-graphics-boot-073.py',
                        'next-experiment/verify-original-graphics-boot-074.py')
anchor = 'print(json.dumps(dict(original_images_independent_hashes=True,'
assert source.count(anchor) == 1
source = source.replace(anchor, '''module_body=entries['graphics-ashmem.ko'][1]
assert len(module_body)==13400 and hashlib.sha256(module_body).hexdigest()=='951e58dceffa3bc00abeab793b4dcbd8d846644d08524e5128aaff7f2c6c493d'
''' + anchor.replace('True,', 'True,ashmem_module_archive_verified=True,'))
anchor = '    evidence = dict('
assert source.count(anchor) == 1
source = source.replace(anchor, r'''    observed_ashmem_loads = [dict(rc=int(rc), errno=int(error))
        for rc, error in re.findall(rb'GRAPHICS074_ASHMEM_LOAD rc=(-?\d+) errno=(\d+) guest_only=1', raw)]
    observed_registered_ashmem_devices = [dict(major=int(major), minor=int(minor), mode=mode.decode())
        for major, minor, mode in re.findall(rb'GRAPHICS074_ASHMEM_DEVICE major=(\d+) minor=(\d+) mode=([0-7]+) kernel_registered=1', raw)]
    assert observed_ashmem_loads == [dict(rc=0, errno=0)]
    assert observed_registered_ashmem_devices
''' + anchor)
source = source.replace('evidence = dict(', '''evidence = dict(
         observed_ashmem_loads=observed_ashmem_loads,
         observed_registered_ashmem_devices=observed_registered_ashmem_devices,
         ''')
compile(source, 'independent-original-ashmem-074', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-ashmem-074', 'exec'))
