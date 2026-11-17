"""Essential458 return guards only, never disk validation suites."""
from pathlib import Path

BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    source = (BASE / 'verify-driver-return-358.py').read_text()
    source = source.replace('commercial61-native-353', 'commercial61-native-458')
    source = source.replace('boot-observation-355.json', 'boot-observation-462.json')
    source = source.replace('post-return-guard-358.json', 'post-return-guard-463.json')
    exec(compile(source, 'verify-driver-return-463.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'verify-driver-return-463.generated.py')))
