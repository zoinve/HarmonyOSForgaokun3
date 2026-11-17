"""Check235 real namespace teardown, marker chain and offline fsck without repair."""
from pathlib import Path
import json

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent

if __name__ == '__main__':
    source = (BASE / 'verify-settings-data-202.py').read_text()
    late = ROOT / 'reports/commercial61-native-235/late-return-observation-240.json'
    assert json.loads(late.read_text())['returned']
    assert source.count("REPORT/'boot-observation.json'") == 1
    source = source.replace("REPORT/'boot-observation.json'", "REPORT/'late-return-observation-240.json'", 1)
    source = source.replace("REPORT=ROOT/'reports/commercial61-native-201'", "REPORT=ROOT/'reports/commercial61-native-235'")
    previous = json.loads((ROOT / 'reports/commercial61-native-206/settings-persistent-analysis-207.json').read_text())['native_boot_id']
    old = "PREVIOUS='76d33584-471a-4e78-bab5-e417a6d5c30b'"
    assert source.count(old) == 1
    source = source.replace(old, 'PREVIOUS=' + repr(previous), 1)
    source = source.replace('settings-data-offline-202', 'settings-data-offline-237')
    source = source.replace('settings-persistent-analysis-202', 'settings-persistent-analysis-237')
    source = source.replace('/mnt/settings202-offline', '/mnt/settings237-offline')
    source = source.replace('settings202-offline-remote', 'settings237-offline-remote')
    old = "    for suffix,data in [('stdout',proc.stdout),('stderr',proc.stderr)]:\n        (REPORT/('settings-data-offline-237.'+suffix)).open('x').write(data)\n"
    assert source.count(old) == 1
    source = source.replace(old,
        "    if proc.stderr:(REPORT/'settings-data-offline-237.stderr').open('x').write(proc.stderr)\n", 1)
    exec(compile(source, 'verify-settings-data-237.generated.py', 'exec'),
         {'__name__': '__main__', '__file__': str(BASE / 'verify-settings-data-237.generated.py')})
