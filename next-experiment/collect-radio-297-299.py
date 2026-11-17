from pathlib import Path
BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    source = (BASE / 'collect-radio-276-279.py').read_text()
    source = source.replace('commercial61-native-276', 'commercial61-native-297')
    source = source.replace('commercial-return-audit-276', 'commercial-return-audit-297').replace('279', '299')
    source = source.replace(repr('266') + ']', repr('266') + ', ' + repr('276') + ', ' + repr('285') + ', ' + repr('294') + ']')
    exec(compile(source, 'collect-radio-297-299.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'collect-radio-297-299.generated.py')))
