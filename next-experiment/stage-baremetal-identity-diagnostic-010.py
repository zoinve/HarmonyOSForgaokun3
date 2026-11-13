"""Stage isolated 010 assets only after archive and diskless ARM64 independent checks."""
from pathlib import Path
import runpy

base=Path(__file__).resolve().parent
source=runpy.run_path(str(base/'stage-baremetal-identity-diagnostic-009.py'),run_name='offline_generator')['source']
for old,new in [('baremetal-identity-diagnostic-009','baremetal-identity-diagnostic-010'),('native-identity-diagnostic-009','native-identity-diagnostic-010'),('baremetal-diagnostic-init-009','baremetal-diagnostic-init-010')]:
    assert old in source;source=source.replace(old,new)
anchor="rows=["
assert source.count(anchor)==1
source=source.replace(anchor,"""archive_check=json.loads((base/'reports/baremetal-diagnostic-init-010/independent-verification.json').read_text())
qemu_check=json.loads((base/'reports/baremetal-mesa-qemu-049/independent-verification.json').read_text())
assert archive_check['binary_helper_kernel_dtb_hashes_verified']
assert qemu_check['missing_render_refusal_and_cleanup_verified'] and qemu_check['missing_optin_refusal_verified']
rows=[
    dict(name='native-mesa-launcher-001',path=work+'/baremetal-diagnostic-init-010/mesa-launcher',sha256=diagnostic['launcher_sha256']),""")
anchor="('diagnostic-init','requires PID 1'),"
assert source.count(anchor)==1
source=source.replace(anchor,"('native-mesa-launcher-001','requires diagnostic kernel and enforcing opt-in'),"+anchor)
compile(source,'stage010-generated','exec')
if __name__=='__main__':exec(compile(source,'stage010-generated','exec'),{'__file__':__file__,'__name__':'__main__'})
