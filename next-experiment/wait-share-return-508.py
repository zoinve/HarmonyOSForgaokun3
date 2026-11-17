"""Observe existing502 only; never retry its boot."""
from pathlib import Path

BASE = Path(__file__).resolve().parent


if __name__ == '__main__':
    source = (BASE / 'wait-bluetooth-return-442.py').read_text()
    source = source.replace('commercial61-native-438','commercial61-native-502')
    source = source.replace('collect-bluetooth-438-441.py','collect-share-502-506.py')
    source = source.replace('boot-observation-441.json','boot-observation-506.json')
    source = source.replace('438 observation expired','502 observation expired')
    exec(compile(source, 'wait-share-return-508.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'wait-share-return-508.generated.py')))
