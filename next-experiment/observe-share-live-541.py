"""Authenticate only532's original restricted read-only debug endpoint."""
from pathlib import Path

BASE=Path(__file__).resolve().parent
if __name__ == '__main__':
    source=(BASE/'observe-radio-live-264.py').read_text().replace('262','532').replace('264','541')
    source=source.replace('time.monotonic() + 120','time.monotonic() + 240')
    exec(compile(source,str(BASE/'observe-share-live-541.generated.py'),'exec'),
         dict(__name__='__main__',__file__=str(BASE/'observe-share-live-541.generated.py')))
