from pathlib import Path
BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    source = (BASE / 'collect-radio-276-279.py').read_text()
    source = source.replace('commercial61-native-276', 'commercial61-native-285')
    source = source.replace('commercial-return-audit-276', 'commercial-return-audit-285')
    source = source.replace('279', '288')
    source = source.replace(repr('266') + ']', repr('266') + ', ' + repr('276') + ']')
    exec(compile(source, 'collect-radio-285-288.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'collect-radio-285-288.generated.py')))
