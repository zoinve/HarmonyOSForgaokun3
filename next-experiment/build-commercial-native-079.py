"""Bring up original WCN6855 firmware/driver; preserve original OOBE lifecycle."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-078.py'))
inner = p['inner']
outer = p['outer'].replace('commercial61-native-078', 'commercial61-native-079').replace('COMMERCIAL078', 'COMMERCIAL079')
anchor = '                native_original();'
assert outer.count(anchor) == 1
outer = outer.replace(anchor, r'''
                char *wifi079[] = {"/sbin/modprobe", "--config", "/etc/modprobe.d", "ath11k_pci", NULL};
                (void)probe("wifi-driver079", wifi079, 15);
                char *net079[] = {"/bin/busybox", "sh", "-c",
                    "echo NETWORK079_KERNEL_OBSERVATION_BEGIN; "
                    "/bin/busybox ls -l /sys/class/net; "
                    "/bin/busybox cat /proc/net/dev /proc/net/route /proc/modules; "
                    "for n in /sys/class/net/*; do echo INTERFACE=$n; "
                    "/bin/busybox ls -l $n/device/driver; "
                    "for a in operstate carrier address; do echo ATTRIBUTE=$a; /bin/busybox cat $n/$a; done; done; "
                    "/bin/busybox dmesg; echo NETWORK079_KERNEL_OBSERVATION_END_NOT_CONNECTIVITY", NULL};
                (void)probe("wifi-observation079", net079, 8);
''' + anchor, 1)
payload = p['payload'].replace('outer=' + repr(p['outer']), 'outer=' + repr(outer), 1).replace(
    'commercial61-native-078', 'commercial61-native-079').replace(
    'commercial-init-desktop-078.py', 'commercial-init-desktop-079.py')
anchor = 'def member(name,mode,data,ino):'
addition = '''
firmware079=root/'native-wifi-firmware-079'
manifest079=json.loads((firmware079/'result.json').read_text())
selected079=[]
for row079 in manifest079['firmware']:
 if '/nfa765/' in row079['path']:continue
 name079='lib/firmware/'+row079['path']
 assert name079 not in entries
 path079=firmware079/row079['path']
 if row079['kind']=='symlink':
  assert str(path079.readlink())==row079['target']
  mode079,data079=stat.S_IFLNK|0o777,row079['target'].encode()
 else:
  data079=path079.read_bytes();assert hashlib.sha256(data079).hexdigest()==row079['sha256']
  mode079=stat.S_IFREG|0o644
 for parent079 in reversed(Path(name079).parents):
  if str(parent079)=='.':continue
  entries.setdefault(str(parent079),(stat.S_IFDIR|0o755,b''))
 entries[name079]=(mode079,data079)
 selected079.append({k:v for k,v in row079.items() if k!='data'})
(local/'wifi-firmware-provenance.json').open('x').write(json.dumps(dict(files=selected079,source_boot_id=manifest079['boot_id'],host_network_modified=False,no_oobe_stop=True,no_activation_state_modified=True),indent=2))
'''
assert payload.count(anchor) == 1
payload = payload.replace(anchor, addition + '\n' + anchor, 1)

if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
