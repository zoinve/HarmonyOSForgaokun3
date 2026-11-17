"""Require an inactive clean data filesystem after the protected USB boot."""
from pathlib import Path

BASE = Path(__file__).resolve().parent

if __name__ == '__main__':
    source = (BASE / 'verify-persistent-data-173.py').read_text()
    source = source.replace("REPORT = ROOT / 'reports/commercial61-native-173'",
                            "REPORT = ROOT / 'reports/commercial61-native-175-compile-fix-1'")
    source = source.replace("number='173'", "number='175'")
    source = source.replace('commercial-workflow-173.py', 'commercial-workflow-175.py')
    exec(compile(source, 'verify-persistent-data-175.generated.py', 'exec'),
         {'__name__':'__main__', '__file__':str(BASE / 'verify-persistent-data-175.generated.py')})
