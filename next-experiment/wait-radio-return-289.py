from pathlib import Path
BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    source = (BASE / 'wait-radio-return-271.py').read_text().replace('266-269', '285-288')
    exec(compile(source, 'wait-radio-return-289.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'wait-radio-return-289.generated.py')))
