"""Recheck Settings BMS/token consistency after206 without exporting tokens."""
from pathlib import Path
import json
import sys

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
if __name__=='__main__':
    assert sys.argv[1:]==['target']
    offline=json.loads((ROOT/'reports/commercial61-native-206/settings-data-offline-212.json').read_text())
    assert offline['filesystem_clean'] and offline['candidate_unchanged_by_offline_inspection']
    manifest=json.loads((ROOT/'reports/commercial61-native-206/runtime-evidence/retrieval-manifest.json').read_text())
    source=(BASE/'audit-settings-live-state-200.py').read_text()
    source=source.replace('settings-live-state-200','settings-live-state-208')
    source=source.replace('/mnt/settings-state200','/mnt/settings-state208')
    source=source.replace('settings-state200-','settings-state208-')
    source=source.replace('41fae8e1ceacedd356da6e6d712aa8a995179c042221657f4d8e2deace9938c6',
        offline['candidate_sha256_after_boot'])
    source=source.replace('commercial61-native-087-76d33584-471a-4e78-bab5-e417a6d5c30b',manifest['run'])
    exec(compile(source,str(__file__),'exec'),{'__name__':'__main__','__file__':str(__file__)})
