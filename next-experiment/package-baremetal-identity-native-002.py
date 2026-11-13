"""Inert native profile-003 assets, separate from the QEMU-only storage kernel."""
from pathlib import Path
import subprocess
import runpy

base=Path(__file__).resolve().parent.parent
report=base/'reports/baremetal-identity-native-package-002'
payload=runpy.run_path(str(Path(__file__).with_name('package-baremetal-identity-native-001.py')))['payload']
payload=payload.replace('baremetal-identity-native-package-001','baremetal-identity-native-package-002')
anchor="candidate=work.parent/'baremetal-identity-candidate-002';out=candidate/'out'"
assert payload.count(anchor)==1
payload=payload.replace(anchor,"candidate=work.parent/'baremetal-identity-profile-003';out=candidate/'out'")
anchor="full=json.loads((candidate/'full-build.json').read_text());assert full['full_build_success'] and full['module_count']==391"
assert payload.count(anchor)==1
payload=payload.replace(anchor,"""full=json.loads((candidate/'result.json').read_text())
assert full['compiled'] and len(full['module_inventory'])==391
assert full['parent_config_unchanged'] and full['source_critical_unchanged'] and full['driver_unchanged']
assert full['enforcing_boot_argument_required']
""")
anchor="audit=json.loads((project/'reports/baremetal-identity-candidate-002/independent-verification.json').read_text())"
assert payload.count(anchor)==1
payload=payload.replace(anchor,"""audit=json.loads((project/'reports/baremetal-identity-profile-003/independent-verification.json').read_text())
assert audit['modules_verified']==391 and audit['artifacts_verified']==6 and audit['config_hashes_verified']
assert audit['local_and_wsl_result_equal']
""")
payload=payload.replace("for row in audit['modules']:","for row in full['module_inventory']:")
anchor="parent=local/'diagnostic-base-002.cpio.gz';parent_sha="
assert payload.count(anchor)==1
payload=payload.replace(anchor,"parent=project/'reports/baremetal-identity-native-package-001/diagnostic-base-002.cpio.gz';parent_sha=")
anchor="(work/'result.json').write_text(json.dumps(d,indent=2)+'\\n')"
assert payload.count(anchor)==1
payload=payload.replace(anchor,"""d['profile']='native-identity-profile-003'
d['enforcing_boot_argument_required']=True
d['legacy_binder_devices']=True
d['contains_test_only_virtio_changes']=False
d['profile_config_sha256']=sha(out/'.config')
assert d['profile_config_sha256']==full['native_config_sha256']
assert d['kernel_sha256']=='4e7796bda71bdc95364276bbff34eb2c72593a2a9a3baa7fe2b9e5ae86e65166'
"""+anchor)
compile(payload,'package-native-identity-002','exec')
if __name__=='__main__':
    assert not report.exists();report.mkdir()
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,capture_output=True,text=True,timeout=240)
    (report/'prepare.stdout').write_text(r.stdout);(report/'prepare.stderr').write_text(r.stderr)
    print(r.stdout);print(r.stderr);raise SystemExit(r.returncode)
