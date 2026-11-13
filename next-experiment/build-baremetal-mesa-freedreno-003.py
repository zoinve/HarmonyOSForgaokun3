"""Enable actual kcmp in an isolated OHOS Mesa build; preserve all earlier build outputs."""
from pathlib import Path
import runpy
import subprocess

base=Path(__file__).resolve().parent.parent
out=base/'reports/baremetal-mesa-freedreno-build-003'


def build_payload():
    source=runpy.run_path(str(Path(__file__).with_name('build-baremetal-mesa-freedreno-002.py')))['build_payload']()
    for old,new in [('baremetal-mesa-freedreno-002','baremetal-mesa-freedreno-003'),
                    ('baremetal-mesa-freedreno-build-002','baremetal-mesa-freedreno-build-003'),
                    ('lab-freedreno002','lab-freedreno003')]:
        assert old in source,old
        source=source.replace(old,new)
    anchor="'-Dauto_features=disabled',"
    assert source.count(anchor)==1
    source=source.replace(anchor,anchor+"'-Dallow-kcmp=enabled',")
    anchor="work.mkdir();stage=work/'stage';build=work/'build'"
    assert source.count(anchor)==1
    source=source.replace(anchor,"""previous=root/'baremetal-mesa-freedreno-002'
assert json.loads((previous/'result.json').read_text())['build_success']
previous_before=tree_hashes(previous)
"""+anchor)
    anchor="assert values['libdir']=='lib64/lab-freedreno003'"
    assert source.count(anchor)==1
    source=source.replace(anchor,anchor+"\n    assert values['allow-kcmp']=='enabled'")
    anchor="    result['source_files_verified_unchanged']=tree_hashes(source)==before"
    assert source.count(anchor)==1
    source=source.replace(anchor,"""    result['previous_build_002_verified_unchanged']=tree_hashes(previous)==previous_before
    result['allow_kcmp_explicitly_enabled']=True
"""+anchor)
    anchor="    assert result['source_files_verified_unchanged'] and result['legacy_prefix_files_verified_unchanged']"
    assert source.count(anchor)==1
    source=source.replace(anchor,anchor+" and result['previous_build_002_verified_unchanged']")
    compile(source,'freedreno-build003','exec')
    return source


if __name__=='__main__':
    payload=build_payload()
    assert not out.exists(), 'Preserve numbered build evidence'
    out.mkdir()
    subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,
                   text=True,check=True,timeout=3100)
