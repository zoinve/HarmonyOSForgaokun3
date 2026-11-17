from pathlib import Path

BASE = Path(__file__).resolve().parent

if __name__ == '__main__':
    source = (BASE / 'observe-radio-live-264.py').read_text()
    source = source.replace('262', '266').replace('264', '268')
    exec(compile(source, 'observe-radio-live-268.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'observe-radio-live-268.generated.py')))
