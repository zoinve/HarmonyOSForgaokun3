"""Losslessly compress completed471 logs only; leave live502 evidence alone."""
from pathlib import Path

BASE = Path(__file__).resolve().parent


if __name__ == '__main__':
    source = (BASE / 'compress-radio-logs-282.py').read_text()
    source = source.replace('radio-log-compression-282.json','cpufreq-log-compression-514.json')
    source = source.replace("['253', '262', '266']", "['471']")
    exec(compile(source, 'compress-cpufreq-logs-514.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'compress-cpufreq-logs-514.generated.py')))
