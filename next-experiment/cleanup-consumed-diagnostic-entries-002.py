"""Archive/remove only consumed 008 after independently verified trial 005 return."""
from pathlib import Path


def launcher_source():
    source=Path(__file__).with_name('cleanup-consumed-diagnostic-entries-001.py').read_text()
    changes={
        'boot-entry-cleanup-001':'boot-entry-cleanup-002',
        'baremetal-native-trial-004-collected':'baremetal-native-trial-005-collected',
        "len(collection['files']) == 116":"len(collection['files']) == 152",
        "(('001', '004'), ('002', '005'), ('003', '006'), ('004', '007'))":"(('005', '008'),)",
        "for v in ('004','005','006','007')":"for v in ('008',)",
    }
    for old,new in changes.items():
        assert old in source,old
        source=source.replace(old,new)
    return source


if __name__=='__main__':
    base=Path(__file__).resolve().parent.parent
    import json
    verified=json.loads((base/'reports/baremetal-native-trial-005-independent-verification.json').read_text())
    assert verified['raw_log_sizes_and_hashes_verified']==152 and verified['one_shot_absent']
    exec(compile(launcher_source(),__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})
