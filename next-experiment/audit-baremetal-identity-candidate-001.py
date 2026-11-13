"""Generate and dry-run an uninstalled reference identity delta; never boot it."""
from pathlib import Path
import json
import subprocess

base = Path(__file__).resolve().parent
reference = Path(r'C:\Users\39255\AppData\Local\Temp\opencode\HarmonyMac-reference-816\ports')
payload = {
    'generator': (reference / 'tools/make-access-token-patch.py').read_text(),
    'driver': {p.name: p.read_text() for p in sorted((reference / 'kernel/accesstokenid').iterdir())
               if p.is_file() and p.name in ('access_tokenid.c', 'access_tokenid.h', 'Kconfig', 'Makefile')},
}
assert len(payload['driver']) == 4
remote = r'''
from pathlib import Path
import hashlib,json,subprocess,sys
p = PAYLOAD
root = Path('/mnt/harmony-lab/work')
source = root/'kernel-source-001/linux'
out = root/'identity-candidate-001'
mount = json.loads(subprocess.check_output(['findmnt','-J','-T',str(root),'-o','SOURCE,UUID'],text=True))['filesystems'][0]
assert mount['source'] == '/dev/nvme0n1p4'
assert mount['uuid'] == '00029cdd-1748-4d2f-b73b-8e8164922098'
assert not out.exists(), 'Never overwrite a numbered candidate'
names = ['include/linux/sched.h','drivers/android/binder_internal.h',
         'include/uapi/linux/android/binder.h','drivers/android/binder.c',
         'drivers/Kconfig','drivers/Makefile']
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
before = {name:sha(source/name) for name in names}
staged = json.loads((root/'kernel-source-001/staging-result.json').read_text())
for name,digest in staged['critical'].items():
    assert sha(source/name) == digest, name
out.mkdir()
generator = out/'make-access-token-patch.py'
generator.write_text(p['generator'])
patch = out/'reference-identity.patch'
subprocess.run([sys.executable,str(generator),str(source),str(patch)],check=True)
driver = out/'accesstokenid';driver.mkdir()
for name,text in p['driver'].items():
    (driver/name).write_text(text)
check = subprocess.run(['patch','--dry-run','--batch','--fuzz=0','-p1','-i',str(patch)],
                       cwd=source,capture_output=True,text=True)
(out/'patch-dry-run.txt').write_text(check.stdout+check.stderr)
after = {name:sha(source/name) for name in names}
assert before == after, 'Source must remain untouched'
report = dict(candidate_directory=str(out),source=str(source),
              source_hashes_before=before,source_hashes_after=after,
              source_unchanged=True,patch_sha256=sha(patch),
              dry_run_returncode=check.returncode,dry_run_output=check.stdout+check.stderr,
              patch_applied=False,compiled=False,sdk7_abi_verified=False,
              driver_ioctl_base='A (0x41); SDK TYPE=84 requests remain unexplained',
              review_required=['SDK7 ioctl sizes/types and feature semantics',
                               'Binder nested transaction and reply identity lifetime',
                               'AccessToken authorization and denial regression tests'],
              boot_entries_modified=False,native_boot_attempted=False)
(out/'audit.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
assert check.returncode == 0, 'Dry-run failed; candidate retained for diagnosis'
'''.replace('PAYLOAD', repr(payload), 1)
report_path = base.parent / 'reports/baremetal-identity-candidate-001.json'
assert not report_path.exists()
result = subprocess.run(['ssh', 'matebook', 'python3 -'], input=remote,
                        text=True, capture_output=True, timeout=180)
(base.parent / 'reports/baremetal-identity-candidate-001.stdout').write_text(result.stdout)
(base.parent / 'reports/baremetal-identity-candidate-001.stderr').write_text(result.stderr)
print(result.stdout, result.stderr)
result.check_returncode()
subprocess.run(['scp', 'matebook:/mnt/harmony-lab/work/identity-candidate-001/audit.json',
                str(report_path)], check=True)
