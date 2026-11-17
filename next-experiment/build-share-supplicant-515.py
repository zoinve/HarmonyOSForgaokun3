"""Enable the file-log option required by the native P2P launch command."""
from pathlib import Path

BASE = Path(__file__).resolve().parent

if __name__ == '__main__':
    source = (BASE / 'build-share-supplicant-499.py').read_text()
    source = source.replace('share-supplicant-499', 'share-supplicant-515')
    anchor = 'CONFIG_CTRL_IFACE=y\n'
    assert source.count(anchor) == 1
    source = source.replace(anchor, anchor + 'CONFIG_DEBUG_FILE=y\n', 1)
    exec(compile(source, str(BASE / 'build-share-supplicant-515.generated.py'), 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'build-share-supplicant-515.generated.py')))
