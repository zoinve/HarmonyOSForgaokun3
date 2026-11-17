"""Add a unique bounded commercial probe; preserve all existing boot files."""
from pathlib import Path
import base64,hashlib,json,subprocess
base=Path(__file__).resolve().parents[1];report=base/'reports/commercial61-native-001'
manifest=json.loads((report/'result.json').read_text())
assert (report/'staged-original-images.json').exists(),'original commercial image transfer must finish first'
artifacts={}
for item in manifest['artifacts']:
 data=subprocess.check_output(['wsl','-d','Debian','--','cat','/home/zoinve/harmony-virgl-883/commercial61-native-001/'+item['name']])
 assert hashlib.sha256(data).hexdigest()==item['sha256']
 if item['name'] in ['init','bootstrap','initrd.img']:artifacts[item['name']]=base64.b64encode(data).decode()
code='payload='+repr(artifacts)+'\n'+r'''
from pathlib import Path
import base64,hashlib,json,os,shutil,subprocess
esp=Path('/boot/efi');root=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/commercial61-native-001')
assert not root.exists();root.mkdir()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
status=subprocess.check_output(['bootctl','status','--no-pager'],text=True)
default='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
assert ('Default Entry: '+default) in status and ('Current Entry: '+default) in status and 'OneShot Entry:' not in status
assert subprocess.run(['systemctl','is-enabled','harmony-lab-screen-off-001.timer'],capture_output=True,text=True).stdout.strip()=='disabled'
assert not subprocess.run(['findmnt','-rn','-S','/dev/nvme0n1p4'],capture_output=True,text=True).stdout.strip()
kernel=esp/'native-original-graphics-031/linux';dtb=esp/'native-original-graphics-031/sc8280xp-huawei-gaokun3.dtb'
assert sha(kernel)=='6fa44a5f1996a82bc95e8c44b3d32a69cc14d3789e39cffa2fcafafb7c294ff5'
assert sha(dtb)=='5f6b1fa73d8bffa1984710d52c0babc4df297cbb90d9f4d9a48a433a104fb016'
images=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/commercial61-original-001')
for n in ['system.img','vendor.img','sysprod.img','chipprod.img']:
 m=json.loads((images/(n+'.json')).read_text());assert sha(images/n)==m['sha256']
before={str(p.relative_to(esp)):sha(p) for p in esp.rglob('*') if p.is_file()}
firmware=subprocess.check_output(['efibootmgr','-v'],text=True)
(root/'installation-journal.json').open('x').write(json.dumps(dict(efi_before=before,firmware=firmware,boot_status=status,timer_disabled=True),indent=2))
for n,data in payload.items():
 with (root/n).open('xb') as f:f.write(base64.b64decode(data));f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o755 if n!='initrd.img' else 0o600)
guards=[]
for n in ['init','bootstrap']:
 r=subprocess.run([str(root/n)],capture_output=True,text=True,timeout=10)
 assert r.returncode==77,(n,r.returncode,r.stderr)
 guards.append(dict(name=n,exit_code=r.returncode,stderr=r.stderr))
dest=esp/'commercial61-native-001';entry=esp/'loader/entries/commercial61-native-001.conf'
assert not dest.exists() and not entry.exists()
assert shutil.disk_usage(esp).free>(root/'initrd.img').stat().st_size+32*1024**2
dest.mkdir()
with (root/'initrd.img').open('rb') as src,(dest/'initrd.img').open('xb') as out:
 shutil.copyfileobj(src,out);out.flush();os.fsync(out.fileno())
assert sha(dest/'initrd.img')==sha(root/'initrd.img')
old=(esp/'loader/entries/harmonyos-gpu-manual.conf').read_text()
options=next(x for x in old.splitlines() if x.startswith('options ')).replace('panic=0','panic=15')+' harmony.commercial=1'
text='\n'.join(['title HarmonyOS commercial ISO - native probe - AUTO RETURN 7 MIN','version 6.0.0.110-original-userland','sort-key zzzz-harmony-commercial','linux /native-original-graphics-031/linux','devicetree /native-original-graphics-031/sc8280xp-huawei-gaokun3.dtb','initrd /commercial61-native-001/initrd.img',options,''])
with entry.open('x') as f:f.write(text);f.flush();os.fsync(f.fileno())
os.sync()
assert all(sha(esp/n)==h for n,h in before.items())
assert subprocess.check_output(['efibootmgr','-v'],text=True)==firmware
assert ('Default Entry: '+default) in subprocess.check_output(['bootctl','status','--no-pager'],text=True)
result=dict(entry=str(entry),entry_text=text,guard_checks=guards,existing_efi_files_unchanged=len(before),
 initrd_sha256=sha(dest/'initrd.img'),free_bytes=shutil.disk_usage(esp).free,ubuntu_default_unchanged=True,
 timer_disabled=True,old_manual_entry_retained=True,one_shot_selected=False,reboot_requested=False,sdk_payload=False)
(root/'installation-result.json').open('x').write(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
'''
r=subprocess.run(['ssh','matebook','sudo -n python3 -'],input=code,text=True,capture_output=True,timeout=400)
(report/'installation.stdout').open('x').write(r.stdout);(report/'installation.stderr').open('x').write(r.stderr)
assert r.returncode==0,r.stderr
(report/'installation-result.json').open('x').write(r.stdout);print(r.stdout)
