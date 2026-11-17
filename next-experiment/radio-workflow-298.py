from pathlib import Path
BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    source = (BASE / 'radio-workflow-295.py').read_text().replace('294', '297').replace('285', '294')
    exec(compile(source, 'radio-workflow-298.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'radio-workflow-298.generated.py')))
