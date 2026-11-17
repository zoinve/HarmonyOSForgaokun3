"""Collect persistent native faults and original UI layout without stopping OOBE."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-085.py'))
inner = p['inner']
outer = p['outer'].replace('commercial61-native-085', 'commercial61-native-086').replace('COMMERCIAL085', 'COMMERCIAL086')
outer = outer.replace('wifi-supplicant-%s085', 'wifi-supplicant-%s086').replace('"/network085-control", pid,', '"/network086-control", pid,')
anchor = 'if(i==7 || i==13)(void)network083_command(child,"freeze");'
assert outer.count(anchor) == 1
outer = outer.replace(anchor, 'if(i==10 || i==13)(void)network083_command(child,"events");', 1)
anchor = '"native-allocator-073.trace","commercial-direct-desktop075.log"'
assert outer.count(anchor) == 1
outer = outer.replace(anchor, anchor + ',"commercial-desktop086.log","native-layout086-100.json","native-layout086-130.json"', 1)
anchor = 'for(unsigned i075=0;i075<3;++i075)'
assert outer.count(anchor) == 1
outer = outer.replace(anchor, 'for(unsigned i075=0;i075<sizeof(names075)/sizeof(names075[0]);++i075)', 1)
payload = p['payload'].replace('outer=' + repr(p['outer']), 'outer=' + repr(outer), 1).replace('commercial61-native-085', 'commercial61-native-086')
payload = payload.replace('commercial-network-helper-085.py', 'commercial-network-helper-086.py').replace('network085-control', 'network086-control')
addition = '''
entries['network085-control']=(stat.S_IFREG|0o755,(work.parent/'commercial61-native-085/network085-control').read_bytes())
layout086=(base/'commercial-layout-086.sh').read_bytes()
entries['native-target/commercial-desktop077.sh']=(stat.S_IFREG|0o755,layout086)
(local/'layout-diagnostic086.sh').open('xb').write(layout086)
(local/'event-reader086.c').open('xb').write((base/'commercial-event-reader-086.c').read_bytes())
'''
anchor = 'def member(name,mode,data,ino):'
assert payload.count(anchor) == 1
payload = payload.replace(anchor, addition + '\n' + anchor, 1)

if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
