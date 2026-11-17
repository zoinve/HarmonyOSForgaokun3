"""Parse the actual public P2P config with a deliberately nonexistent driver."""
from pathlib import Path
import gzip
import json
import runpy
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
BUILD=Path('/home/zoinve/harmony-virgl-883')

def probe(config):
    with tempfile.TemporaryDirectory(prefix='share-config-531-') as directory:
        path=Path(directory)/'public.conf'
        path.write_bytes(config)
        binary=BUILD/'share-supplicant-515/wpa_supplicant/wpa_supplicant'
        result=subprocess.run(['qemu-aarch64',str(BUILD/'native-wpa-083/lib/ld-linux-aarch64.so.1'),
            '--library-path',str(BUILD/'native-wpa-083/usr/lib/aarch64-linux-gnu'),str(binary),
            '-Dshare531_nonexistent','-ip2p0','-c'+str(path)],capture_output=True,text=True,timeout=20)
        text=result.stdout+result.stderr
        return dict(exit_status=result.returncode,unknown_update_config="unknown global field 'update_config=0'" in text,
                    config_read_failed='Failed to read or parse configuration' in text,
                    nonexistent_driver_rejected="Unsupported driver 'share531_nonexistent'" in text)

if __name__ == '__main__':
    parser=runpy.run_path(str(ROOT/'next-experiment/audit-commercial-network-inputs-079.py'))['members']
    entries={name:data for name,mode,data in parser(gzip.decompress(
        (BUILD/'commercial61-native-517/minimal-overlay.img').read_bytes()))}
    original=entries['native-target/share501/p2p.conf']
    assert original.count(b'update_config=0\n')==1
    corrected=original.replace(b'update_config=0\n',b'',1)
    old,new=probe(original),probe(corrected)
    assert old['unknown_update_config'] and old['config_read_failed'],old
    assert not new['config_read_failed'] and not new['unknown_update_config'] and new['nonexistent_driver_rejected'],new
    result=dict(prior517=old,corrected=new,radio_opened=False,real_p2p_verified=False)
    with (ROOT/'reports/share-config-531.json').open('x') as stream:json.dump(result,stream,indent=2)
    print(json.dumps(result,indent=2))
