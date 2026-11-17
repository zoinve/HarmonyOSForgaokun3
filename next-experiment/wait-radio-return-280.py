from pathlib import Path

BASE = Path(__file__).resolve().parent

if __name__ == '__main__':
    source = (BASE / 'wait-radio-return-271.py').read_text()
    source = source.replace('266-269', '276-279')
    exec(compile(source, 'wait-radio-return-280.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'wait-radio-return-280.generated.py')))
