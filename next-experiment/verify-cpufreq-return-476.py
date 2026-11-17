"""Essential Ubuntu return/identity guards, no disk verification suite."""
from pathlib import Path

BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    source = (BASE / 'verify-driver-return-358.py').read_text()
    source = source.replace('commercial61-native-353', 'commercial61-native-471')
    source = source.replace('boot-observation-355.json', 'boot-observation-475.json')
    source = source.replace('post-return-guard-358.json', 'post-return-guard-476.json')
    exec(compile(source, 'verify-cpufreq-return-476.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'verify-cpufreq-return-476.generated.py')))
