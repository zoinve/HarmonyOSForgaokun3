"""A distinct second boot with byte-identical binaries and the SAME data file."""
from pathlib import Path
import json
import hashlib

ROOT=Path(__file__).resolve().parents[1]
BUILD=Path('/home/zoinve/harmony-virgl-883')
def sha(data):return hashlib.sha256(data).hexdigest()

if __name__=='__main__':
    prior=ROOT/'reports/commercial61-native-166-compile-fix-1'
    check=json.loads((prior/'persistent-offline-verification.json').read_text())
    assert check['filesystem_clean'] and check['disk_marker_matches_native_runtime'] and check['lab_partition_unmounted']
    assert all(json.loads((prior/'admission-test.json').read_text()).values())
    parent=BUILD/'commercial61-native-166-compile-fix-1'
    work=BUILD/'commercial61-native-167'
    report=ROOT/'reports/commercial61-native-167'
    assert not work.exists() and not report.exists()
    metadata=json.loads((prior/'result.json').read_text())
    overlay=json.loads((prior/'overlay-result.json').read_text())
    for row in metadata['artifacts']:assert sha((parent/row['name']).read_bytes())==row['sha256']
    assert sha((parent/'minimal-overlay.img').read_bytes())==overlay['sha256']
    work.mkdir();report.mkdir()
    for row in metadata['artifacts']:(work/row['name']).open('xb').write((parent/row['name']).read_bytes())
    (work/'minimal-overlay.img').open('xb').write((parent/'minimal-overlay.img').read_bytes())
    overlay['chain'][-1]='commercial61-native-167/initrd.img'
    overlay['ordered_chain_equals_full_167']=overlay.pop('ordered_chain_equals_full_166')
    overlay['changed_from_full_parent']=[]
    metadata['persistent167']=dict(binaries_identical_to_166=True,data_file_reused_without_reset=True,
        expected_previous_native_boot_id=check['native_boot_id'],cross_boot_persistence_verified=False)
    for folder in [work,report]:
        (folder/'result.json').open('x').write(json.dumps(metadata,indent=2))
        (folder/'overlay-result.json').open('x').write(json.dumps(overlay,indent=2))
    print(json.dumps(metadata['persistent167'],indent=2))
