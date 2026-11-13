"""One isolated KVM parser experiment; no physical GPU, disks, network or reboot."""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess

BASE = Path(__file__).resolve().parent
OUT = BASE.parent / 'reports/composer-parser-run-001'
PACKAGE = BASE.parent / 'reports/composer-parser-package-001'
REMOTE = '/home/zoinve/.local/share/harmony-arm64-kvm-lab/official-arm-sdk-921/composer-parser-runtime-001'


def main():
    assert not OUT.exists(), OUT
    manifest = json.loads((PACKAGE / 'manifest.json').read_text())
    archive = PACKAGE / 'initramfs.cpio.gz'
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == manifest['initrd_sha256']
    spec = importlib.util.spec_from_file_location('parser_builder', BASE / 'build-composer-parser-001.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    kernel = '/home/zoinve/.local/share/harmony-arm64-kvm-lab/system-882/Image'
    command = builder.qemu_command(kernel, REMOTE + '/initramfs.cpio.gz')
    runner = '''from pathlib import Path
import hashlib,json,os,subprocess,time
OUT=Path(REMOTE)
def snapshot():
    files={str(p):hashlib.sha256(p.read_bytes()).hexdigest()
           for p in Path('/boot/efi/loader').rglob('*.conf')}
    return dict(boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
                cmdline=Path('/proc/cmdline').read_text().strip(),
                kernel=os.uname().release,loader_configs=files,
                screenoff_enabled=subprocess.check_output(['systemctl','is-enabled','harmony-lab-screen-off-001.timer'],text=True).strip(),
                screenoff_active=subprocess.check_output(['systemctl','is-active','harmony-lab-screen-off-001.timer'],text=True).strip())
assert not (OUT/'result.json').exists()
before=snapshot()
assert before['kernel']=='7.1.0-rc3-gaokun3+' and 'harmony.diag=1' not in before['cmdline']
assert before['screenoff_enabled']=='enabled' and before['screenoff_active']=='active'
assert not list(Path('/boot/efi/loader/entries').glob('harmony-native-diag-*.conf'))
assert hashlib.sha256(Path(KERNEL).read_bytes()).hexdigest()=='fb9dffc643f64c754c4a7a34e6fd3b9de6d60bd1ed2ba2aa6096f25bf7ad5474'
assert hashlib.sha256((OUT/'initramfs.cpio.gz').read_bytes()).hexdigest()==DIGEST
for p in Path('/proc').iterdir():
    if not p.name.isdecimal():continue
    try:exe=(p/'exe').resolve(strict=True).name
    except (FileNotFoundError,PermissionError,ProcessLookupError):continue
    assert not exe.startswith('qemu-system-'),str(p)
gpu='/home/zoinve/.local/share/harmony-arm64-kvm-lab/gpu-host-probe-883'
start=time.monotonic()
with (OUT/'serial.log').open('xb') as serial,(OUT/'stderr.log').open('xb') as err:
    child=subprocess.Popen(COMMAND,stdout=serial,stderr=err,env=dict(os.environ,QEMU_MODULE_DIR=gpu+'/modules',LD_LIBRARY_PATH=gpu+'/root/usr/lib/aarch64-linux-gnu'))
    timed_out=False
    try:rc=child.wait(timeout=90)
    except subprocess.TimeoutExpired:
        timed_out=True;child.terminate()
        try:rc=child.wait(timeout=10)
        except subprocess.TimeoutExpired:child.kill();rc=child.wait(timeout=10)
after=snapshot()
text=(OUT/'serial.log').read_text(errors='replace')
cases=[line for line in text.splitlines() if line.startswith('PARSER001_CASE ')]
result=dict(command=COMMAND,returncode=rc,timed_out=timed_out,elapsed_seconds=time.monotonic()-start,
            before=before,after=after,host_preserved=before==after,cases=cases,
            probe_pass='PARSER001_PASS cases=8 original_code=1 factory_called=0 payload_not_parsed=1 smq_not_tested=1 desktop_not_tested=1' in text,
            child_exit_zero=any('USERSPACE_EXIT' in l and 'completed=1 status=0' in l for l in text.splitlines()),
            disks_attached=0,gpu_attached=False,network_attached=False,desktop_verified=False)
with (OUT/'result.json').open('x') as f:json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
'''
    runner = ('REMOTE=' + repr(REMOTE) + '\nKERNEL=' + repr(kernel) +
              '\nDIGEST=' + repr(manifest['initrd_sha256']) + '\nCOMMAND=' + repr(command) + '\n' + runner)
    compile(runner, 'composer-parser-runner-001', 'exec')
    OUT.mkdir()
    with (OUT / 'runner.py').open('x') as f:
        f.write(runner)
    subprocess.run(['ssh', 'matebook', 'mkdir ' + REMOTE], check=True, timeout=30)
    for source, name in [(archive, 'initramfs.cpio.gz'), (OUT / 'runner.py', 'runner.py')]:
        subprocess.run(['scp', str(source), 'matebook:' + REMOTE + '/' + name], check=True, timeout=120)
    with (OUT / 'host.stdout').open('xb') as stdout, (OUT / 'host.stderr').open('xb') as stderr:
        p = subprocess.run(['ssh', 'matebook', 'sudo -n python3 ' + REMOTE + '/runner.py'],
                           stdout=stdout, stderr=stderr, timeout=150)
    for name in ('serial.log', 'stderr.log', 'result.json'):
        subprocess.run(['scp', 'matebook:' + REMOTE + '/' + name, str(OUT / name)], check=True, timeout=60)
    result = json.loads((OUT / 'result.json').read_text())
    print(json.dumps(result, indent=2))
    assert p.returncode == 0 and result['returncode'] == 0 and not result['timed_out']
    assert result['probe_pass'] and result['child_exit_zero'] and result['host_preserved']
    assert len(result['cases']) == 8 and all('pass=1' in c for c in result['cases'])


if __name__ == '__main__':
    main()
