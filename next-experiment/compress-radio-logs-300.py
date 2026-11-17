from pathlib import Path

BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    source = (BASE / 'compress-radio-logs-282.py').read_text()
    source = source.replace('radio-log-compression-282.json', 'radio-log-compression-300.json')
    source = source.replace("['253', '262', '266']", "['276', '285', '294']")
    exec(compile(source, 'compress-radio-logs-300.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'compress-radio-logs-300.generated.py')))
