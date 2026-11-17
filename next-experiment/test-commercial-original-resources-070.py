"""Exact asset provenance, unsafe ZIP rejection and archive admission."""
from pathlib import Path
import ast
import hashlib
import io
import json
import runpy
import stat
import zipfile

b=Path(__file__).resolve().parent
h=runpy.run_path(str(b/'commercial-original-resources-070.py'))
hap=(b.parent/'reports/commercial-ui-resources-audit-068/HwStartupGuide.hap').read_bytes()
files=h['rawfiles'](hap)
assert len(files)==46 and sum(map(len,files.values()))==6402165
for name in ['resources/rawfile/../escape','resources/rawfile/a//b','resources/rawfile/a\\b','resources/rawfile/a"b']:
    data=io.BytesIO()
    with zipfile.ZipFile(data,'w') as archive:
        archive.writestr(name,b'x')
    blob=data.getvalue()
    try:
        h['rawfiles'](blob,hashlib.sha256(blob).hexdigest())
    except AssertionError:
        pass
    else:
        raise AssertionError(name)
data=io.BytesIO()
with zipfile.ZipFile(data,'w') as archive:
    info=zipfile.ZipInfo('resources/rawfile/link')
    info.create_system=3
    info.external_attr=(stat.S_IFLNK|0o777)<<16
    archive.writestr(info,b'/etc/passwd')
blob=data.getvalue()
try:
    h['rawfiles'](blob,hashlib.sha256(blob).hexdigest())
except AssertionError:
    pass
else:
    raise AssertionError('symlink accepted')
old=runpy.run_path(str(b/'build-commercial-native-069.py'))
new=runpy.run_path(str(b/'build-commercial-native-070.py'))
assert new['inner']==h['instrument'](old['inner'],files)
assert new['outer'].replace('commercial61-native-070','commercial61-native-069').replace('COMMERCIAL070','COMMERCIAL069')==old['outer']
assert 'mount("overlay","/system","overlay",MS_RDONLY,options)' in new['inner']
tree=ast.parse(runpy.run_path(str(b/'build-native-return-overlay-033.py'))['payload'])
helpers={}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))],type_ignores=[]),'archive-helpers','exec'),helpers)
root=Path('/home/zoinve/harmony-virgl-883')
before=helpers['parse'](root/'commercial61-native-069/initrd.img')
after=helpers['parse'](root/'commercial61-native-070/initrd.img')
assert set(before)<=set(after)
changed=sorted(n for n in before if before[n]!=after[n])
assert changed==['init','native-target/bootstrap'],changed
expected,added=h['add_entries'](before,files)
assert set(after)-set(before)==set(added)
assert all(after[n]==entry for n,entry in added.items())
assert all(stat.S_IMODE(after[h['PREFIX']+n][0])==0o444 for n in files)
manifest=dict(exact_original_rawfiles=True,rawfile_count=len(files),rawfile_bytes=sum(map(len,files.values())),
    all_original_members_unchanged_except_init_bootstrap=True,exact_delta_existing=changed,
    added_members=sorted(added),readonly_overlay=True,no_installed_record_changes=True,
    no_private_abi_hooks=True,extractor_negative_tests_passed=True,
    runtime_resolution_verified=False,desktop_verified=False)
with (b.parent/'reports/commercial61-native-070/admission-test.json').open('x') as f:
    json.dump(manifest,f,indent=2)
print(json.dumps(manifest,indent=2))
