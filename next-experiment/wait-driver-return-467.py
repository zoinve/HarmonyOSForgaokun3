"""Wait for the existing manual458 boot only; never request another boot."""
from pathlib import Path

BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    source = (BASE / 'wait-bluetooth-return-442.py').read_text()
    source = source.replace('commercial61-native-438', 'commercial61-native-458')
    source = source.replace('collect-bluetooth-438-441.py', 'collect-driver-458-462.py')
    source = source.replace('boot-observation-441.json', 'boot-observation-462.json')
    source = source.replace('438 observation expired', '458 observation expired')
    exec(compile(source, 'wait-driver-return-467.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'wait-driver-return-467.generated.py')))
