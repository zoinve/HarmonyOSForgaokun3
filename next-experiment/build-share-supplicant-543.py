"""Build the official2.12 P2P backend with file logging and real WPA handling."""
from pathlib import Path

BASE=Path(__file__).resolve().parent
if __name__ == '__main__':
    source=(BASE/'build-share-supplicant-499.py').read_text()
    source=source.replace('share-supplicant-499','share-supplicant-543')
    source=source.replace('share-supplicant-patch-497.py','share-supplicant-patch-544.py')
    source=source.replace("'rev-parse', 'HEAD'","'rev-parse', 'hostap_2_12^{commit}'")
    anchor='CONFIG_CTRL_IFACE=y\n'
    assert source.count(anchor)==1
    source=source.replace(anchor,anchor+'CONFIG_DEBUG_FILE=y\n',1)
    exec(compile(source,str(BASE/'build-share-supplicant-543.generated.py'),'exec'),
         dict(__name__='__main__',__file__=str(BASE/'build-share-supplicant-543.generated.py')))
