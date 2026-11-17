"""Prepare the private controller probe with the corrected official2.12 backend."""
from pathlib import Path

BASE=Path(__file__).resolve().parent
if __name__ == '__main__':
    source=(BASE/'build-compat-native-542.py').read_text()
    source=source.replace('542','546').replace('share-supplicant-515','share-supplicant-543')
    exec(compile(source,str(BASE/'build-compat-native-546.wrapper.py'),'exec'),
         dict(__name__='__main__',__file__=str(BASE/'build-compat-native-546.wrapper.py')))
