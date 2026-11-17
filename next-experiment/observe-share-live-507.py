"""Authenticate only the existing502 read-only native endpoint."""
from pathlib import Path

BASE = Path(__file__).resolve().parent


if __name__ == '__main__':
    source = (BASE / 'observe-radio-live-264.py').read_text().replace('262','502').replace('264','507')
    source = source.replace('time.monotonic() + 120', 'time.monotonic() + 240')
    exec(compile(source, 'observe-share-live-507.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'observe-share-live-507.generated.py')))
