"""Observe/retrieve471 only, excluding every earlier canonical run."""
from pathlib import Path

BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    source = (BASE / 'collect-radio-276-279.py').read_text()
    source = source.replace('commercial61-native-276', 'commercial61-native-471')
    source = source.replace('commercial-return-audit-276', 'commercial-return-audit-471').replace('279', '475')
    source = source.replace(repr('266') + ']', repr('266') + ', ' + ', '.join(repr(x) for x in
        ['276', '285', '294', '297', '306', '321', '331', '341', '353', '365', '378', '385', '394', '401', '420', '438', '458']) + ']')
    exec(compile(source, 'collect-cpufreq-471-475.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'collect-cpufreq-471-475.generated.py')))
