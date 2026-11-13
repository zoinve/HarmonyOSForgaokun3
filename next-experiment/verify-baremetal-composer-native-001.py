"""Read-only method evidence verification; never launches an operational script."""
from pathlib import Path
import hashlib,json
b=Path(__file__).resolve().parent.parent
c=b/'reports/baremetal-native-trial-012-collected'
m=json.loads((c/'collection.json').read_text())
assert len(m['files'])==378
old=json.loads((b/'reports/baremetal-native-trial-011-collected/collection.json').read_text())
current={r['path']:r for r in m['files']}
assert all(current[r['path']]==r for r in old['files'])
for r in m['files']:
 p=c/r['path'];assert not Path(r['path']).is_absolute() and '..' not in Path(r['path']).parts
 data=p.read_bytes();assert len(data)==r['bytes'] and hashlib.sha256(data).hexdigest()==r['sha256']
new=[r for r in m['files'] if r['path'].split('/')[0] not in m['before']['prior_log_directories']]
assert len(new)==38 and len({r['path'].split('/')[0] for r in new})==1
last=max(new,key=lambda r:r['path']);text=(c/last['path']).read_text()
markers=[
 'NATIVE_DIAGNOSTIC_BEGIN release=7.1.0-rc3-gaokun3-el2',
 'initrd=\\harmony-native-diag-015\\initrd.img',
 'NATIVE_MESA001_SANDBOX uid=65534 gid=65534 groups=0 caps=0 no_new_privs=1 private_pid_mount_net=1 primary_node_absent=1 policy_loaded_by_probe=0',
 'COMPOSER001_GL renderer=FD690',
 'COMPOSER001_CONTRACT actual_reference_methods=1 caller_fds_closed=1 held_fd_closed=1 no_init_display=1 no_commit=1',
 'COMPOSER001_CONSUMER pid=2 reference_fence_wait_success=1 center=255,0,0,255 background=0,0,255,255 imported_fd_closed=1',
 'COMPOSER001_TRANSFER producer=1 consumer=2 exec_consumer=1 sender_transfer_fds_closed=1 consumer_imported_fd_closed=1',
 'COMPOSER001_PIXELS center=255,0,0,255 corner=0,0,255,255',
 'COMPOSER001_MAPPED center_8_8=255,0,0,255 corner_0_8=0,0,255,255',
 'COMPOSER001_PASS cross_process_dmabuf_and_native_fence desktop_not_tested=1',
 'NATIVE_MESA001_END status=0 desktop_verified=0',
]
for marker in markers:assert marker in text,marker
assert text.count('COMPOSER001_PASS')==1
result=dict(trial='012',candidate='015',native_log=last,raw_hashes_verified=len(m['files']),
 historical_records_preserved=len(old['files']),new_snapshots=len(new),verified_markers=markers,
 method_bridge_verified=True,full_hdi_abi_verified=False,renderservice_verified=False,
 scanout_verified=False,desktop_verified=False,selinux_policy_authorization_verified=False,
 initially_unsignaled_fence_verified=False)
out=b/'reports/baremetal-composer-native-001.json'
assert not out.exists()
with out.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result,indent=2))
