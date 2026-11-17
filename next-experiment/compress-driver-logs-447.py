"""Losslessly compress completed438 logs using the established226 reader format."""
from pathlib import Path

BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    source = (BASE / 'compress-radio-logs-282.py').read_text()
    source = source.replace('radio-log-compression-282.json', 'driver-log-compression-447.json')
    source = source.replace("['253', '262', '266']", "['438']")
    exec(compile(source, 'compress-driver-logs-447.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'compress-driver-logs-447.generated.py')))
