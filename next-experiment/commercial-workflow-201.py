'''One new Settings launch experiment on the verified evolved candidate state.'''
from pathlib import Path
import json
import runpy
import sys

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
REPORT=ROOT/'reports/commercial61-native-201'
PREVIOUS=runpy.run_path(str(BASE/'commercial-workflow-197.py'))
OPERATIONS=PREVIOUS['OPERATIONS']
configure_local_transport=PREVIOUS['configure_local_transport']


def source201(operation):
    source=PREVIOUS['source197'](operation)
    changes=[('commercial61-native-197-r1','commercial61-native-201'),
             ('commercial61-native-197','commercial61-native-201'),
             ('commercial-return-audit-197','commercial-return-audit-201'),
             ('ordered_chain_equals_full_197','ordered_chain_equals_full_201'),
             ('estimated197','estimated201'),('set197.img','set201.img'),
             ('settings197_preflight','settings201_preflight'),
             ('native isolated original Settings state recovery 197','native original Settings launch and teardown diagnostics 201'),
             ('f315f5adf08f31d1c99be3a3c11f23cf256a642b83e179d406cbf72e9abd36ce',
              '41fae8e1ceacedd356da6e6d712aa8a995179c042221657f4d8e2deace9938c6')]
    for old,new in changes:source=source.replace(old,new)
    if operation=='run-commercial-native':
        old=json.loads((ROOT/'reports/commercial61-native-197-r1/overlay-result.json').read_text())['sha256']
        new=json.loads((REPORT/'overlay-result.json').read_text())['sha256']
        assert source.count(old)==1
        source=source.replace(old,new,1)
    elif operation=='retrieve-commercial-evidence':
        run=json.loads((ROOT/'reports/commercial61-native-197-r1/runtime-evidence/retrieval-manifest.json').read_text())['run']
        anchor='if p.name not in ['
        assert source.count(anchor)==1 and run not in source
        source=source.replace(anchor,anchor+repr(run)+', ',1)
    return source


if __name__=='__main__':
    assert len(sys.argv)==2 and sys.argv[1] in (*OPERATIONS,'retain-entries')
    admission=json.loads((REPORT/'admission-test.json').read_text())
    assert admission and all(admission.values())
    offline=json.loads((ROOT/'reports/commercial61-native-197-r1/settings-data-offline-199.json').read_text())
    assert offline['filesystem_clean'] and offline['active165_unchanged_from_predeployment']
    configure_local_transport()
    if sys.argv[1]=='retain-entries':
        path=BASE/'retain-latest-experiment-boot-entries-001.py'
        source=path.read_text();assert source.count('commercial[-2:]')==1
        source=source.replace('commercial[-2:]',
            "[p for p in commercial if p.name in {'commercial61-native-173.conf','commercial61-native-201.conf'}]",1)
        source=source.replace('assert all((entries/n).is_file() for n in keep)',
            'assert len(keep)==4 and all((entries/n).is_file() for n in keep)',1)
        exec(compile(source,str(path),'exec'),{'__name__':'__main__','__file__':str(path)})
    else:
        operation=sys.argv[1];source=source201(operation)
        assert source==(REPORT/(operation+'.generated.py')).read_text()
        exec(compile(source,operation,'exec'),{'__name__':'__main__','__file__':str(BASE/(operation+'-201.py'))})
