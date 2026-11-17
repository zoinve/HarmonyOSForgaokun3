"""Retain real 084 association; independently observe probes and freeze stacks."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-084.py'))
inner = p['inner']
outer = p['outer'].replace('commercial61-native-084', 'commercial61-native-085').replace('COMMERCIAL084', 'COMMERCIAL085')
outer = outer.replace('wifi-supplicant-%s084', 'wifi-supplicant-%s085').replace('"/network084-control", pid,', '"/network085-control", pid,')
anchor = '                if(i==4 && !started083)(void)network083_command(child,"log");'
assert outer.count(anchor) == 1
outer = outer.replace(anchor, '''                if(i==7 && started083){
                    (void)network083_command(child,"http");
                    (void)network083_command(child,"https");
                }
                if(i==7 || i==13)(void)network083_command(child,"freeze");
''' + anchor, 1)
payload = p['payload'].replace('outer=' + repr(p['outer']), 'outer=' + repr(outer), 1).replace('commercial61-native-084', 'commercial61-native-085')
# Only the generated helper changes; the genuine private connection stays at 084.
payload = payload.replace("commercial-network-helper-084.py", "commercial-network-helper-085.py").replace('network084-control', 'network085-control')
anchor = 'def member(name,mode,data,ino):'
assert payload.count(anchor) == 1
payload = payload.replace(anchor, "entries['network084-control']=(stat.S_IFREG|0o755,(work.parent/'commercial61-native-084/network084-control').read_bytes())\n\n" + anchor, 1)

if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
