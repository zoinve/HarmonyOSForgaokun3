"""Apply the verified173 teardown analysis with the current boot predecessor."""
from pathlib import Path

BASE = Path(__file__).resolve().parent

if __name__ == '__main__':
    source = (BASE / 'analyze-persistent-data-173.py').read_text()
    source = source.replace("REPORT = ROOT / 'reports/commercial61-native-173'",
                            "REPORT = ROOT / 'reports/commercial61-native-175-compile-fix-1'")
    source = source.replace('reports/commercial61-native-168/persistent-runtime-analysis.json',
                            'reports/commercial61-native-173/persistent-runtime-analysis.json')
    exec(compile(source, 'analyze-persistent-data-175.generated.py', 'exec'),
         {'__name__':'__main__', '__file__':str(BASE / 'analyze-persistent-data-175.generated.py')})
