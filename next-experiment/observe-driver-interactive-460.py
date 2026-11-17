"""Confirm the user-requested458 live endpoint without starting another boot."""
from pathlib import Path

BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    source = (BASE / 'observe-radio-live-264.py').read_text().replace('262', '458').replace('264', '460')
    exec(compile(source, 'observe-driver-interactive-460.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'observe-driver-interactive-460.generated.py')))
