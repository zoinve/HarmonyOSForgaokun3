from pathlib import Path

BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    source = (BASE / 'collect-radio-276-279.py').read_text()
    source = source.replace('commercial61-native-276', 'commercial61-native-294')
    source = source.replace('commercial-return-audit-276', 'commercial-return-audit-294')
    source = source.replace('279', '296')
    source = source.replace(repr('266') + ']', repr('266') + ', ' + repr('276') + ', ' + repr('285') + ']')
    exec(compile(source, 'collect-radio-294-296.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'collect-radio-294-296.generated.py')))
