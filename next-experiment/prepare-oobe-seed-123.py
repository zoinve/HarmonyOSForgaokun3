"""Stage a minimal original-schema seed on the target; export metadata only."""
from pathlib import Path
import base64
import gzip
import hashlib
import json
import runpy
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent

if __name__ == '__main__':
    report = ROOT / 'reports/oobe-seed-preparation-123'
    assert not report.exists()
    inspection = json.loads((ROOT / 'reports/oobe-snapshot-inspection-122/result.json').read_text())
    assert inspection['source_snapshot_unchanged'] and not inspection['settings_modified']
    original = Path('/home/zoinve/harmony-virgl-883/commercial61-native-116/initrd.img')
    metadata = json.loads((ROOT / 'reports/commercial61-native-116/result.json').read_text())
    expected = next(a['sha256'] for a in metadata['artifacts'] if a['name'] == 'initrd.img')
    assert hashlib.sha256(original.read_bytes()).hexdigest() == expected
    parser = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    matches = [data for name, mode, data in parser(gzip.decompress(original.read_bytes()))
               if name == 'native-target/scratch-data.ext4']
    assert len(matches) == 1
    pristine = matches[0]
    expected_pristine = '0eff50c2bf203de7e8e1d446dc8af1c858993cdf951aff8e0d46a690c8e2ea89'
    assert len(pristine) == 536870912 and hashlib.sha256(pristine).hexdigest() == expected_pristine
    reference = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-ed213a0')
    assert subprocess.check_output(['git', '-C', str(reference), 'rev-parse', 'HEAD'], text=True).strip() == 'ed213a08817c642e9b455fb7d8f5271da41631eb'
    upstream = subprocess.check_output(['git', '-C', str(reference), 'show', 'HEAD:ports/tools/prepare-oobe-settings.py'])
    code = '\n'.join([
        'EXPECTED_SNAPSHOT_SHA123=' + repr(inspection['source_snapshot_sha256']),
        'EXPECTED_PRISTINE_SHA123=' + repr(expected_pristine),
        'EXPECTED_UPSTREAM_SHA123=' + repr(hashlib.sha256(upstream).hexdigest()),
        'PRISTINE_GZIP_BASE64123=' + repr(base64.b64encode(gzip.compress(pristine, mtime=0)).decode()),
        'UPSTREAM_SOURCE_BASE64123=' + repr(base64.b64encode(upstream).decode()),
        (BASE / 'prepare-oobe-seed-123-remote.py').read_text()])
    compile(code, 'seed123-remote', 'exec')
    report.mkdir()
    (report / 'remote-source.py').open('x').write((BASE / 'prepare-oobe-seed-123-remote.py').read_text())
    (report / 'input-provenance.json').open('x').write(json.dumps(dict(
        snapshot_sha256=inspection['source_snapshot_sha256'], pristine_sha256=expected_pristine,
        upstream_prepare_sha256=hashlib.sha256(upstream).hexdigest(), source_schema_is_original=True), indent=2))
    runpy.run_path(str(BASE / 'commercial-workflow-121.py'))['configure_local_transport']()
    result = subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes',
        '-o','HostName=192.168.10.128','-o','HostKeyAlias=192.168.10.128','matebook','sudo -n python3 -'],
        input=code,text=True,capture_output=True,timeout=300)
    (report / 'stdout').open('x').write(result.stdout)
    (report / 'stderr').open('x').write(result.stderr)
    assert result.returncode == 0, result.stderr
    parsed = json.loads(result.stdout)
    assert parsed['only_local_first_run_settings_modified'] and not parsed['commercial_activation_modified']
    (report / 'result.json').open('x').write(json.dumps(parsed, indent=2))
    print(result.stdout)
