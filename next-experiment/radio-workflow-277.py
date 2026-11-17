from pathlib import Path

BASE = Path(__file__).resolve().parent

if __name__ == '__main__':
    source = (BASE / 'radio-workflow-263.py').read_text().replace('262', '276')
    old = '.replace(' + repr('235') + ', ' + repr('253') + ')'
    new = '.replace(' + repr('235') + ', ' + repr('266') + ')'
    assert source.count(old) == 1
    source = source.replace(old, new, 1)
    exec(compile(source, 'radio-workflow-277.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'radio-workflow-277.generated.py')))
