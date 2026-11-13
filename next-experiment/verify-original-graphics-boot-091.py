"""Independent larger-volume hash and actual free-space/account observations."""
from pathlib import Path
import re
import runpy

parent = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-090.py')))
inspect_frame = parent['inspect_frame']
decode_commit_result = parent['decode_commit_result']


def parse_state_records(raw):
    return parent['parse_state_records'](raw.replace(b'GRAPHICS091_STATE ', b'GRAPHICS090_STATE '))


def parse_data_capacity(raw):
    rows = []
    for sample, status, error, fragment, blocks, available in re.findall(
            rb'GRAPHICS091_DATA_CAPACITY sample=(\d+) stat=(-?\d+) errno=(\d+) fragment=(\d+) blocks=(\d+) available=(\d+)', raw):
        success = int(status) == 0 and int(error) == 0
        rows.append(dict(sample=int(sample), stat=int(status), errno=int(error),
                         fragment=int(fragment), blocks=int(blocks), available=int(available),
                         available_bytes=int(fragment) * int(available) if success else None))
    return rows


source = parent['source']
assert source.count("number='090', tag='090'") == 1
source = source.replace("number='090', tag='090'", "number='091', tag='091'")
source = source.replace('GRAPHICS090_', 'GRAPHICS091_')
assert source.count('baremetal-sdk-original-init-qemu-090') == 2
source = source.replace('baremetal-sdk-original-init-qemu-090', 'baremetal-sdk-original-init-qemu-091')
source = source.replace('next-experiment/verify-original-graphics-boot-090.py',
                        'next-experiment/verify-original-graphics-boot-091.py')
anchor = '    evidence = dict('
assert source.count(anchor) == 1
source = source.replace(anchor, '''    scratch = result['scratch_data']
    assert scratch['freshly_formatted'] and scratch['disk_backed'] and scratch['test_only']
    assert not scratch['ram_backed'] and not scratch['original_userdata_attached']
    assert scratch['bytes'] == 8*1024*1024*1024 and scratch['retained_copy_verified']
    expected = '/home/zoinve/harmony-virgl-883/baremetal-sdk-original-init-qemu-' + number + '/scratch-data.ext4'
    assert scratch['retained_path'] == expected
    check = "from pathlib import Path; import hashlib,json,sys; p=Path(sys.argv[1]); assert p.is_file() and not p.is_symlink(); f=p.open('rb'); h=hashlib.file_digest(f,'sha256').hexdigest(); f.close(); print(json.dumps(dict(bytes=p.stat().st_size,sha256=h)))"
    volume_checked = subprocess.run(['wsl','-d','Debian','--','python3','-c',check,expected],
                             capture_output=True,text=True,timeout=180)
    volume_checked.check_returncode()
    independent_larger_data_volume = json.loads(volume_checked.stdout)
    assert independent_larger_data_volume['bytes'] == 8*1024*1024*1024
    assert independent_larger_data_volume['sha256'] == scratch['after_sha256']
    observed_data_capacity = runpy.run_path(str(BASE / 'next-experiment/verify-original-graphics-boot-091.py'))['parse_data_capacity'](raw)
''' + anchor)
source = source.replace('evidence = dict(', '''evidence = dict(
         independent_larger_data_volume=independent_larger_data_volume,
         observed_data_capacity=observed_data_capacity,
         ''', 1)
compile(source, 'independent-original-data-capacity-091', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-data-capacity-091', 'exec'))
