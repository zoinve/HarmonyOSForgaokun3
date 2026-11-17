"""Collect the one502 run, excluding all already retrieved experiment runs."""
from pathlib import Path

BASE = Path(__file__).resolve().parent


if __name__ == '__main__':
    source = (BASE / 'collect-cpufreq-471-475.py').read_text()
    source = source.replace('commercial61-native-471', 'commercial61-native-502')
    source = source.replace('commercial-return-audit-471', 'commercial-return-audit-502')
    source = source.replace("'458']", "'458', '471']")
    source = source.replace(".replace('279', '475')", ".replace('279', '506')")
    exec(compile(source, 'collect-share-502-506.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'collect-share-502-506.generated.py')))
