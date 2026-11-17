"""Prune fully shadowed initrds, preserving the exact tested 123 filesystem."""
from pathlib import Path
import gzip
import hashlib
import json
import lzma
import runpy
import subprocess

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
BUILD=Path('/home/zoinve/harmony-virgl-883')
report=ROOT/'reports/commercial61-native-124'
assert not report.exists()
report.mkdir()
parse=runpy.run_path(str(BASE/'audit-commercial-network-inputs-079.py'))['members']
def unpack(data):
    raw=lzma.decompress(data) if data.startswith(b'\xfd7zXZ') else gzip.decompress(data)
    return {n:(mode,body) for n,mode,body in parse(raw)}
chain=json.loads((ROOT/'reports/commercial61-native-123/overlay-result.json').read_text())['chain']
archives={}
for relative in chain:
    number,filename=relative.split('/')
    if filename=='early094.img': path=BUILD/'commercial61-native-094/minimal-overlay.img'
    elif number=='commercial61-native-001': path=BUILD/relative
    elif number=='commercial61-native-016': path=BUILD/'commercial61-native-016-r2/minimal-overlay.img'
    elif number=='commercial61-native-072': path=BUILD/number/'minimal-overlay-xz.img'
    else: path=BUILD/number/'minimal-overlay.img'
    data=path.read_bytes()
    archives[relative]=(hashlib.sha256(data).hexdigest(),unpack(data))
seen=set();kept=[]
for relative in reversed(chain):
    names=set(archives[relative][1])
    if not names<=seen:
        kept.append(relative)
        seen.update(names)
kept.reverse()
merged={}
for relative in kept: merged.update(archives[relative][1])
assert merged==unpack((BUILD/'commercial61-native-123/initrd.img').read_bytes())
assert len(kept)<len(chain)
proof=dict(previous_chain=chain,chain=kept,removed_fully_shadowed=[r for r in chain if r not in kept],
    exact_full_123_filesystem_match=True,payloads_unchanged=True,
    hashes={relative:archives[relative][0] for relative in kept})
(report/'admission-test.json').open('x').write(json.dumps(proof,indent=2))
runpy.run_path(str(BASE/'commercial-workflow-123.py'))['configure_local_transport']()
remote='proof='+repr(proof)+'\n'+r'''
from pathlib import Path
import hashlib,json,os,subprocess
esp=Path('/boot/efi');parent=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab')
work=parent/'commercial61-native-124'
def sha(p):
 with p.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
status=subprocess.check_output(['bootctl','status','--no-pager'],text=True)
default='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
assert ('Default Entry: '+default) in status and ('Current Entry: '+default) in status and 'OneShot Entry:' not in status
for command,expected in [('is-enabled','enabled'),('is-active','active')]:
 assert subprocess.check_output(['systemctl',command,'harmony-lab-screen-off-001.timer'],text=True).strip()==expected
assert not subprocess.run(['findmnt','-rn','-S','/dev/nvme0n1p4'],capture_output=True,text=True).stdout.strip()
assert not work.exists()
for relative,expected in proof['hashes'].items():assert sha(esp/relative)==expected
assert sha(parent/'oobe-seed-123/seed.ext4')=='02c810f94799cf4b89cc59dea2409981b4678e8b201d60c0ceb62fd7397b21cd'
old=(esp/'loader/entries/commercial61-native-123.conf').read_text().splitlines()
lines=[]
for line in old:
 if line.startswith('initrd ') and line.split(' ',1)[1].lstrip('/') not in proof['chain']:continue
 if line.startswith('title '):line='title HarmonyOS original-schema OOBE seed 124 - AUTO RETURN 270 SEC'
 lines.append(line)
options=next(line[8:] for line in lines if line.startswith('options '))
required=['harmony.commercial=1','harmony.original_init_test=1','harmony.native_original=1','enforcing=0','ohos.boot.hardware=matebookego','panic=15']
assert all(token in options.split() for token in required)
# The EFI stub prepends initrd= arguments; leave margin below arm64's 2048 bytes.
estimated=len(options)+sum(len('initrd=\\'+r.replace('/','\\'))+1 for r in proof['chain'])+1
assert estimated<1800,estimated
entry=esp/'loader/entries/commercial61-native-124.conf'
text='\n'.join(lines)+'\n'
assert len(text.encode())<os.statvfs(esp).f_frsize
assert not entry.exists() and __import__('shutil').disk_usage(esp).free>=32*1024**2+8192
before={str(p.relative_to(esp)):sha(p) for p in esp.rglob('*') if p.is_file()}
firmware=subprocess.check_output(['efibootmgr','-v'],text=True)
work.mkdir(mode=0o700)
with (work/'installation-journal.json').open('x') as out:
 json.dump(dict(efi_before=before,firmware=firmware,boot_status=status,timer_enabled=True),out,indent=2);out.flush();os.fsync(out.fileno())
with entry.open('x') as out:out.write(text);out.flush();os.fsync(out.fileno())
os.sync()
assert all(sha(esp/n)==h for n,h in before.items())
assert subprocess.check_output(['efibootmgr','-v'],text=True)==firmware
result=dict(entry=str(entry),entry_text=text,initrd_sha256=sha(esp/'commercial61-native-123/initrd.img'),
 estimated_kernel_cmdline_bytes=estimated,payloads_unchanged=True,exact_full_123_filesystem_match=True)
(work/'installation-result.json').open('x').write(json.dumps(result,indent=2))
print(json.dumps(result))
'''
r=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','HostName=192.168.10.128','-o','HostKeyAlias=192.168.10.128','matebook','sudo -n python3 -'],input=remote,text=True,capture_output=True,timeout=180)
assert r.returncode==0,r.stderr
(report/'installation-result.json').open('x').write(r.stdout)
for operation in ['run-commercial-native','retrieve-commercial-evidence','verify-commercial-return']:
    source=(ROOT/'reports/commercial61-native-123'/f'{operation}.generated.py').read_text().replace('commercial61-native-123','commercial61-native-124').replace('commercial-return-audit-123','commercial-return-audit-124')
    if operation=='retrieve-commercial-evidence':
        anchor='if p.name not in ['
        assert source.count(anchor)==1
        source=source.replace(anchor,anchor+repr('commercial61-native-087-8a37e4cd-deb7-433f-bbb0-fdd51847fba0')+', ',1)
    if operation=='verify-commercial-return':
        source=source.replace("esp/'commercial61-native-124/initrd.img'","esp/'commercial61-native-123/initrd.img'")
    compile(source,operation,'exec')
    (report/f'{operation}.generated.py').open('x').write(source)
print(json.dumps(dict(original_initrd_count=len(chain),pruned_initrd_count=len(kept),installation=json.loads(r.stdout)),indent=2))
