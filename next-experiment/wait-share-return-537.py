"""Observe532's sole boot; an observation timeout never requests a retry."""
from pathlib import Path

BASE=Path(__file__).resolve().parent
if __name__ == '__main__':
    source=(BASE/'wait-bluetooth-return-442.py').read_text()
    source=source.replace('commercial61-native-438','commercial61-native-532')
    source=source.replace('collect-bluetooth-438-441.py','collect-share-532-536.py')
    source=source.replace('boot-observation-441.json','boot-observation-536.json')
    source=source.replace('438 observation expired','532 observation expired')
    exec(compile(source,str(BASE/'wait-share-return-537.generated.py'),'exec'),
         dict(__name__='__main__',__file__=str(BASE/'wait-share-return-537.generated.py')))
