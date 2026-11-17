from pathlib import Path
BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    source = (BASE / 'collect-radio-276-279.py').read_text()
    source = source.replace('commercial61-native-276', 'commercial61-native-306')
    source = source.replace('commercial-return-audit-276', 'commercial-return-audit-306').replace('279', '308')
    source = source.replace(repr('266') + ']', repr('266') + ', ' + repr('276') + ', ' + repr('285') + ', ' + repr('294') + ', ' + repr('297') + ']')
    exec(compile(source, 'collect-input-306-308.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'collect-input-306-308.generated.py')))
