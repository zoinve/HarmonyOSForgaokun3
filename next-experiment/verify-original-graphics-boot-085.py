"""Attribute genuine notification events without inferring parser acceptance."""
from pathlib import Path
import runpy

parent = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-084.py')))
inspect_frame = parent['inspect_frame']
decode_commit_result = parent['decode_commit_result']


def parse_state_records(raw):
    return parent['parse_state_records'](raw.replace(b'GRAPHICS085_STATE ', b'GRAPHICS084_STATE '))


def parse_profile_events(raw):
    return parent['parse_profile_events'](raw.replace(b'GRAPHICS085_PROFILE_EVENT ', b'GRAPHICS084_PROFILE_EVENT '))


source = parent['source']
assert source.count("number='084', tag='084'") == 1
source = source.replace("number='084', tag='084'", "number='085', tag='085'")
source = source.replace('GRAPHICS084_', 'GRAPHICS085_')
source = source.replace('baremetal-sdk-original-init-qemu-084', 'baremetal-sdk-original-init-qemu-085')
source = source.replace('next-experiment/verify-original-graphics-boot-084.py',
                        'next-experiment/verify-original-graphics-boot-085.py')
compile(source, 'independent-original-profile-events-085', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-profile-events-085', 'exec'))
