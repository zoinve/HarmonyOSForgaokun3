from pathlib import Path
BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    source = (BASE / 'radio-workflow-277.py').read_text()
    source = source.replace('276', '285').replace('266', '276')
    exec(compile(source, 'radio-workflow-286.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'radio-workflow-286.generated.py')))
