"""Test authenticated, restricted native SSH in a separate Ubuntu loopback fixture.

This does not boot HarmonyOS, attach a debugger, or alter the host SSH service.
No existing host private key is read or copied. A fixture host key stays on-device.
"""
from pathlib import Path
import base64
import hashlib
import json
import re
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
BUILD = Path('/home/zoinve/harmony-virgl-883/live-debug-reader-156')
REPORT = ROOT / 'reports/live-debug-156'
SSH = '/mnt/c/Windows/System32/OpenSSH/ssh.exe'
KEY = 'C:/Users/39255/.ssh/id_ed25519_opencode_matebook'
PORT = 22256
REMOTE_ROOT = '/home/zoinve/.local/share/harmony-arm64-kvm-lab/live-debug-156'
OUTER = [SSH, '-i', KEY, '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
         '-o', 'HostKeyAlias=192.168.10.128', '-o', 'ConnectTimeout=8']

PREPARE = r'''
from pathlib import Path
import base64,hashlib,json,os,re,socket,stat,subprocess,time
record=json.loads(INPUT_RECORD)
root=Path(REMOTE_ROOT)
assert os.geteuid()==0 and not root.exists()
with socket.socket() as guard:
 guard.bind(('127.0.0.1',22256))
root.mkdir(mode=0o700)
jail=root/'root'
jail.mkdir(mode=0o700)
tools=['/usr/sbin/sshd','/usr/lib/openssh/sshd-auth','/usr/lib/openssh/sshd-session']
paths=set(tools)
ldd={}
for tool in tools:
 result=subprocess.run(['ldd',tool],check=True,capture_output=True,text=True)
 assert 'not found' not in result.stdout
 ldd[tool]=result.stdout
 for line in result.stdout.splitlines():
  match=re.search(r'(?:=>\s+)?(/\S+)\s+\(0x[0-9a-f]+\)',line)
  if match:paths.add(match.group(1))
assert '/lib/ld-linux-aarch64.so.1' in paths
files=[]
for name in sorted(paths):
 data=Path(name).read_bytes()
 assert data[:4]==b'\x7fELF' and int.from_bytes(data[18:20],'little')==183
 target=jail/name.lstrip('/')
 target.parent.mkdir(parents=True,exist_ok=True)
 target.write_bytes(data);target.chmod(0o755)
 files.append(dict(path=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
reader=base64.b64decode(record['reader'],validate=True)
assert hashlib.sha256(reader).hexdigest()==record['reader_sha256']
(jail/'bin').mkdir()
(jail/'bin/diag').write_bytes(reader);(jail/'bin/diag').chmod(0o755)
for name in ['etc/diag','etc/ssh','root','run/sshd','logs','dev']:
 (jail/name).mkdir(parents=True,exist_ok=True)
(jail/'etc/passwd').write_text('root:x:0:0:diagnostic:/root:/bin/diag\nsshd:x:65534:65534:privsep:/run/sshd:/bin/diag\n')
(jail/'etc/group').write_text('root:x:0:\nsshd:x:65534:\n')
(jail/'etc/diag/authorized_keys').write_text('restrict '+record['public_key']+'\n')
(jail/'etc/diag/authorized_keys').chmod(0o600)
os.mknod(jail/'dev/null',stat.S_IFCHR|0o666,os.makedev(1,3))
key=jail/'etc/diag/host_ed25519'
subprocess.run(['/usr/bin/ssh-keygen','-q','-t','ed25519','-N','','-C','live-debug-156','-f',str(key)],check=True,capture_output=True)
host_public=key.with_suffix('.pub').read_text().split()
host_public=' '.join(host_public[:2])
config="""
Port 22256
ListenAddress 127.0.0.1
HostKey /etc/diag/host_ed25519
PidFile /run/sshd.pid
AuthorizedKeysFile /etc/diag/authorized_keys
AuthenticationMethods publickey
PubkeyAuthentication yes
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitEmptyPasswords no
PermitRootLogin prohibit-password
UsePAM no
UseDNS no
AllowUsers root
StrictModes yes
DisableForwarding yes
PermitTTY no
PermitUserEnvironment no
PermitUserRC no
ForceCommand read-only
MaxSessions 1
MaxAuthTries 2
MaxStartups 2:30:3
LoginGraceTime 10
ClientAliveInterval 10
ClientAliveCountMax 1
PrintMotd no
LogLevel VERBOSE
""".strip()+'\n'
(jail/'etc/ssh/sshd_config').write_text(config)
fixture='SYNTHETIC_FIXTURE_ONLY not a HarmonyOS observation\nStartAbility ability:com.huawei.hmos.settings/fixture\nbundle not exist -n com.huawei.hmos.settings -u 100 fixture\n'
(jail/'logs/hilog').write_text(fixture)
(jail/'logs/native').write_text('fixture only\n')
checked=subprocess.run(['chroot',str(jail),'/usr/sbin/sshd','-t','-f','/etc/ssh/sshd_config'],capture_output=True,text=True)
assert checked.returncode==0,checked.stderr
effective=subprocess.run(['chroot',str(jail),'/usr/sbin/sshd','-T','-f','/etc/ssh/sshd_config'],check=True,capture_output=True,text=True).stdout
expected=['listenaddress 127.0.0.1:22256','authenticationmethods publickey','passwordauthentication no',
 'kbdinteractiveauthentication no','disableforwarding yes','permittty no','forcecommand read-only','usepam no']
assert all(line in effective.splitlines() for line in expected)
version=subprocess.run(['/usr/sbin/sshd','-V'],capture_output=True,text=True).stderr.strip()
result=dict(root=str(root),fixture_only=True,harmony_boot_performed=False,original_service_configuration_changed=False,
 ubuntu_default_or_network_configuration_changed=False,private_keys_exported=False,host_public_key=host_public,
 reader_sha256=record['reader_sha256'],files=files,ldd=ldd,config=config,effective_config=effective,version=version)
(root/'preparation.json').write_text(json.dumps(result,indent=2))
log=(root/'sshd.log').open('xb')
proc=subprocess.Popen(['/usr/bin/timeout','--signal=TERM','--kill-after=3','180',
 'chroot',str(jail),'/usr/sbin/sshd','-D','-e','-f','/etc/ssh/sshd_config'],
 stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
result['supervisor_pid']=proc.pid
result['supervisor_starttime']=Path('/proc/'+str(proc.pid)+'/stat').read_text().split()[21]
(root/'supervisor.json').write_text(json.dumps(dict(pid=proc.pid,starttime=result['supervisor_starttime'])))
for _ in range(30):
 if proc.poll() is not None:raise RuntimeError((root/'sshd.log').read_text())
 with socket.socket() as probe:
  probe.settimeout(.2)
  if probe.connect_ex(('127.0.0.1',22256))==0:break
 time.sleep(.1)
else:raise RuntimeError('fixture listener did not start')
print(json.dumps(result))
'''

STOP = r'''
from pathlib import Path
import json,os,signal,socket,time
root=Path(REMOTE_ROOT)
record=json.loads((root/'supervisor.json').read_text())
pid=record['pid'];proc=Path('/proc')/str(pid)
if proc.exists():
 assert (proc/'stat').read_text().split()[21]==record['starttime']
 command=(proc/'cmdline').read_bytes().split(b'\0')
 assert command[0]==b'/usr/bin/timeout' and str(root/'root').encode() in command
 os.killpg(pid,signal.SIGTERM)
for _ in range(40):
 with socket.socket() as probe:
  probe.settimeout(.2)
  if probe.connect_ex(('127.0.0.1',22256))!=0:break
 time.sleep(.1)
else:raise RuntimeError('fixture listener still active')
print(json.dumps(dict(listener_stopped=True,private_keys_exported=False,sshd_log=(root/'sshd.log').read_text())))
'''


def remote(source, timeout=60):
    source = source.replace('REMOTE_ROOT', repr(REMOTE_ROOT))
    result = subprocess.run([*OUTER, 'zoinve@192.168.10.128', 'sudo -n python3 -'],
        input=source, text=True, capture_output=True, timeout=timeout)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def main():
    assert not REPORT.exists() and not BUILD.exists(), 'preserve numbered evidence'
    tests = subprocess.run(['python3', str(ROOT / 'next-experiment/test-live-debug-reader-156.py')], capture_output=True, timeout=20)
    assert tests.returncode == 0, tests.stderr.decode()
    BUILD.mkdir()
    binary = BUILD / 'reader'
    compiled = subprocess.run(['aarch64-linux-gnu-gcc','-static','-Os','-s','-Wall','-Wextra','-Werror',
        str(ROOT / 'next-experiment/live-debug-reader-156.c'),'-o',str(binary)],capture_output=True,timeout=60)
    assert compiled.returncode == 0, compiled.stderr.decode()
    data = binary.read_bytes()
    assert data[:4] == b'\x7fELF' and int.from_bytes(data[18:20], 'little') == 183
    public = Path('/mnt/c/Users/39255/.ssh/id_ed25519_opencode_matebook.pub').read_text().split()
    assert public[0] == 'ssh-ed25519' and re.fullmatch(r'[A-Za-z0-9+/=]+', public[1])
    record = dict(reader=base64.b64encode(data).decode(), reader_sha256=hashlib.sha256(data).hexdigest(),
                  public_key=' '.join(public[:2]))
    REPORT.mkdir()
    (REPORT / 'reader-tests.stderr').write_bytes(tests.stderr)
    (REPORT / 'reader-compile.stderr').write_bytes(compiled.stderr)
    prepared = None
    tunnel = None
    result = dict(fixture_only=True, harmony_boot_performed=False, reader_tests_pass=True)
    try:
        prepared = remote(PREPARE.replace('INPUT_RECORD', repr(json.dumps(record))))
        (REPORT / 'preparation.json').open('x').write(json.dumps(prepared, indent=2))
        known = REPORT / 'known_hosts'
        known.open('x').write('live-debug-156 ' + prepared['host_public_key'] + '\n')
        known_windows = subprocess.check_output(['wslpath','-w',str(known)],text=True).strip()
        tunnel = subprocess.Popen([*OUTER,'-N','-o','ExitOnForwardFailure=yes','-L',
            '127.0.0.1:22256:127.0.0.1:22256','zoinve@192.168.10.128'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        client = [SSH,'-i',KEY,'-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes',
            '-o','HostKeyAlias=live-debug-156','-o','UserKnownHostsFile='+known_windows,
            '-o','ConnectTimeout=2','-p',str(PORT)]
        def query(command, extra=None):
            return subprocess.run([*client,*(extra or []),'root@127.0.0.1',command],capture_output=True,text=True,timeout=10)
        for _ in range(12):
            status = query('status')
            if status.returncode == 0:break
            if tunnel.poll() is not None:raise RuntimeError(tunnel.communicate()[1].decode(errors='replace'))
            time.sleep(.3)
        assert status.returncode == 0, status.stderr
        status_rows = [json.loads(line) for line in status.stdout.splitlines()]
        assert status_rows[0]['log'] == 'hilog' and status_rows[0]['available']
        settings = query('settings')
        assert settings.returncode == 0, settings.stderr
        events = [json.loads(line)['event'] for line in settings.stdout.splitlines()]
        assert events == ['settings_launch_requested','settings_bundle_absent_user100','settings_read_complete'],events
        rejected = {}
        for command in ['sh','status; id','settings\nstatus','scp -t file']:
            attempt = query(command)
            assert attempt.returncode == 77 and 'command_refused' in attempt.stderr,(command,attempt)
            rejected[command] = attempt.returncode
        denied = query('status',['-o','PubkeyAuthentication=no','-o','PreferredAuthentications=password',
            '-o','NumberOfPasswordPrompts=0'])
        assert denied.returncode == 255 and 'Permission denied' in denied.stderr,denied
        forward = subprocess.run([*client,'-W','127.0.0.1:22256','root@127.0.0.1'],capture_output=True,text=True,timeout=10)
        assert forward.returncode != 0 and 'administratively prohibited' in forward.stderr,forward
        result.update(authenticated_status_verified=True,host_key_pinned=True,
            native_arm64_forced_reader_verified=True,synthetic_settings_events=events,
            rejected_commands=rejected,unauthenticated_access_denied=True,forwarding_denied=True,
            full_harmony_debugger_attached=False,native_harmony_live_channel_verified=False)
    finally:
        if tunnel is not None:
            tunnel.terminate()
            try:tunnel.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                tunnel.kill();tunnel.communicate(timeout=5)
        # Even a preparation error may have started the bounded fixture.
        if prepared is not None:
            stopped = remote(STOP)
            (REPORT / 'stop.json').open('x').write(json.dumps(stopped, indent=2))
            result['fixture_listener_stopped'] = stopped['listener_stopped']
        (REPORT / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
