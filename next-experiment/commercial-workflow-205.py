"""One new longer bounded boot on the evolved candidate, not the desktop data."""
from pathlib import Path
import json
import runpy
import sys

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
REPORT=ROOT/'reports/commercial61-native-205'
PREVIOUS=runpy.run_path(str(BASE/'commercial-workflow-201.py'))
OPERATIONS=PREVIOUS['OPERATIONS']
configure_local_transport=PREVIOUS['configure_local_transport']


def source205(operation):
    source=PREVIOUS['source201'](operation)
    for old,new in [('commercial61-native-201','commercial61-native-205'),
        ('commercial-return-audit-201','commercial-return-audit-205'),
        ('ordered_chain_equals_full_201','ordered_chain_equals_full_205'),
        ('estimated201','estimated205'),('set201.img','set205.img'),
        ('settings201_preflight','settings205_preflight'),
        ('native original Settings launch and teardown diagnostics 201','native original BMS recovery and readiness-gated Settings 205'),
        ('41fae8e1ceacedd356da6e6d712aa8a995179c042221657f4d8e2deace9938c6',
         'e7e18b21f4e1d0d6a4acd652edc13b64c0ab4f3540ea6ddb155ea107f4e57fb4')]:
        source=source.replace(old,new)
    if operation=='run-commercial-native':
        old=json.loads((ROOT/'reports/commercial61-native-201/overlay-result.json').read_text())['sha256']
        new=json.loads((REPORT/'overlay-result.json').read_text())['sha256']
        assert source.count(old)==1 and source.count('time.monotonic()+660')==1
        source=source.replace(old,new,1).replace('time.monotonic()+660','time.monotonic()+1260',1)
        source=source.replace('within 11 minutes','within 21 minutes')
    elif operation=='retrieve-commercial-evidence':
        run=json.loads((ROOT/'reports/commercial61-native-201/runtime-evidence/retrieval-manifest.json').read_text())['run']
        anchor='if p.name not in ['
        assert source.count(anchor)==1 and run not in source
        source=source.replace(anchor,anchor+repr(run)+', ',1)
    return source


if __name__=='__main__':
    assert len(sys.argv)==2 and sys.argv[1] in (*OPERATIONS,'retain-entries')
    admission=json.loads((REPORT/'admission-test.json').read_text())
    assert admission and all(admission.values())
    offline=json.loads((ROOT/'reports/commercial61-native-201/settings-data-offline-202.json').read_text())
    assert offline['full_native_storage_acceptance'] and offline['active165_unchanged_from_predeployment']
    configure_local_transport()
    if sys.argv[1]=='retain-entries':
        path=BASE/'retain-latest-experiment-boot-entries-001.py'
        source=path.read_text();assert source.count('commercial[-2:]')==1
        source=source.replace('commercial[-2:]',
            "[p for p in commercial if p.name in {'commercial61-native-173.conf','commercial61-native-205.conf'}]",1)
        source=source.replace('assert all((entries/n).is_file() for n in keep)',
            'assert len(keep)==4 and all((entries/n).is_file() for n in keep)',1)
        exec(compile(source,str(path),'exec'),{'__name__':'__main__','__file__':str(path)})
    else:
        operation=sys.argv[1];source=source205(operation)
        assert source==(REPORT/(operation+'.generated.py')).read_text()
        exec(compile(source,operation,'exec'),{'__name__':'__main__','__file__':str(BASE/(operation+'-205.py'))})
