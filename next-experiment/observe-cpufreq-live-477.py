"""Authenticate the existing471 read-only debug endpoint."""
from pathlib import Path

BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    source = (BASE / 'observe-radio-live-264.py').read_text().replace('262', '471').replace('264', '477')
    exec(compile(source, 'observe-cpufreq-live-477.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'observe-cpufreq-live-477.generated.py')))
