"""Wait for existing471 attempt; never request a second boot."""
from pathlib import Path

BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    source = (BASE / 'wait-bluetooth-return-442.py').read_text()
    source = source.replace('commercial61-native-438', 'commercial61-native-471')
    source = source.replace('collect-bluetooth-438-441.py', 'collect-cpufreq-471-475.py')
    source = source.replace('boot-observation-441.json', 'boot-observation-475.json')
    source = source.replace('438 observation expired', '471 observation expired')
    exec(compile(source, 'wait-cpufreq-return-478.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'wait-cpufreq-return-478.generated.py')))
