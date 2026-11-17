from pathlib import Path

BASE = Path(__file__).resolve().parent

if __name__ == '__main__':
    source = (BASE / 'analyze-radio-266-274.py').read_text()
    source = source.replace('commercial61-native-266', 'commercial61-native-276')
    source = source.replace('radio-analysis-274.json', 'radio-analysis-284.json')
    source = source.replace("r'/vendor/bin/hdf_devhost -i 5 -n blue_host'",
        "r'COMMERCIAL001_PROCESS [^\\n]*cmd=blue_host\\s+-i 5 -n blue_host'")
    marker = '        hilog_available=bool(hilogs),'
    addition = '''        vendor_operations=[dict(operation=operation, result=int(result), errno=int(error), uid=int(uid))
            for operation, result, error, uid in re.findall(
                r'QcaTransport276[^\\n]*operation=([A-Za-z_0-9]+) result=(-?\\d+) errno=(\\d+) uid=(\\d+)', hilog)],
'''
    assert source.count(marker) == 1
    source = source.replace(marker, addition + marker, 1)
    exec(compile(source, 'analyze-radio-276-284.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'analyze-radio-276-284.generated.py')))
