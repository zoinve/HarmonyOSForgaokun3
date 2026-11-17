from pathlib import Path
BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    source = (BASE / 'radio-workflow-295.py').read_text().replace('294', '306').replace('285', '297')
    source = source.replace('native Bluetooth entry diagnostics 306', 'native Bluetooth and multitouch observation 306')
    exec(compile(source, 'input-workflow-307.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'input-workflow-307.generated.py')))
