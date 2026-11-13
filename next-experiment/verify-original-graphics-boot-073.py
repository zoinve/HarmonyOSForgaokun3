"""Keep original-identity/hash checks; record actual names and wait states."""
from pathlib import Path
import runpy

parent = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-072.py')))


def parse_state_records(raw):
    return parent['parse_state_records'](raw.replace(b'GRAPHICS073_STATE ', b'GRAPHICS072_STATE '))


source = parent['source']
assert source.count("number='072', tag='072'") == 1
source = source.replace("number='072', tag='072'", "number='073', tag='073'")
source = source.replace('GRAPHICS072_', 'GRAPHICS073_')
source = source.replace('next-experiment/verify-original-graphics-boot-072.py',
                        'next-experiment/verify-original-graphics-boot-073.py')
assert source.count('(wchan|syscall)') == 1
source = source.replace('(wchan|syscall)', '(comm|wchan|syscall)')
compile(source, 'independent-original-workers-073', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-workers-073', 'exec'))
