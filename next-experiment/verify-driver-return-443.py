"""Essential438 return protection checks; no disk validation suites."""
from pathlib import Path

BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    source = (BASE / 'verify-driver-return-358.py').read_text()
    source = source.replace('commercial61-native-353', 'commercial61-native-438')
    source = source.replace('boot-observation-355.json', 'boot-observation-441.json')
    source = source.replace('post-return-guard-358.json', 'post-return-guard-443.json')
    exec(compile(source, 'verify-driver-return-443.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'verify-driver-return-443.generated.py')))
