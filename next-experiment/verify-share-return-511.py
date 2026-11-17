"""Essential post-return guards only; no historical filesystem suite."""
from pathlib import Path

BASE = Path(__file__).resolve().parent


if __name__ == '__main__':
    source = (BASE / 'verify-driver-return-358.py').read_text()
    source = source.replace('commercial61-native-353','commercial61-native-502')
    source = source.replace('boot-observation-355.json','boot-observation-506.json')
    source = source.replace('post-return-guard-358.json','post-return-guard-511.json')
    exec(compile(source, 'verify-share-return-511.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'verify-share-return-511.generated.py')))
