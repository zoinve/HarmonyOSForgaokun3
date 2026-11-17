"""Authenticate438's existing read-only diagnostic status endpoint."""
from pathlib import Path

BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    source = (BASE / 'observe-radio-live-264.py').read_text().replace('262', '438').replace('264', '444')
    exec(compile(source, 'observe-bluetooth-live-444.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'observe-bluetooth-live-444.generated.py')))
