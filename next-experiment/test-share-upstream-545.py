"""Check2.12 provenance, required fixes, CLI flags and the public config parser."""
from pathlib import Path
import gzip
import json
import runpy
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
BUILD=Path('/home/zoinve/harmony-virgl-883')
SOURCE=Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/hostap-share-reference-495')
PIN='831364bf02710ad09c2f27d3efa92abeeb5634c0'

if __name__ == '__main__':
    output=ROOT/'reports/share-upstream-545.json'
    assert not output.exists()
    assert subprocess.check_output(['git','-C',str(SOURCE),'rev-parse','hostap_2_12^{commit}'],text=True).strip()==PIN
    fixes=['65d865e6','b0b23f99']
    for fix in fixes:
        subprocess.run(['git','-C',str(SOURCE),'merge-base','--is-ancestor',fix,PIN],check=True)
    binary=BUILD/'share-supplicant-543/wpa_supplicant/wpa_supplicant'
    command=['qemu-aarch64',str(BUILD/'native-wpa-083/lib/ld-linux-aarch64.so.1'),
        '--library-path',str(BUILD/'native-wpa-083/usr/lib/aarch64-linux-gnu'),str(binary)]
    version=subprocess.run(command+['-f','/dev/null','-v'],capture_output=True,text=True,timeout=20)
    text=version.stdout+version.stderr
    assert version.returncode==0 and 'wpa_supplicant v2.12' in text and 'usage:' not in text.lower()
    parser=runpy.run_path(str(ROOT/'next-experiment/audit-commercial-network-inputs-079.py'))['members']
    entries={name:data for name,mode,data in parser(gzip.decompress(
        (BUILD/'commercial61-native-532/minimal-overlay.img').read_bytes()))}
    config=entries['native-target/share501/p2p.conf']
    assert b'update_config=' not in config
    with tempfile.TemporaryDirectory(prefix='share-upstream-545-') as directory:
        path=Path(directory)/'public.conf'
        path.write_bytes(config)
        result=subprocess.run(command+['-Dshare545_nonexistent','-ip2p0','-c'+str(path)],
            capture_output=True,text=True,timeout=20)
        text=result.stdout+result.stderr
        assert 'Failed to read or parse configuration' not in text
        assert "Unsupported driver 'share545_nonexistent'" in text
    patch=runpy.run_path(str(ROOT/'next-experiment/share-supplicant-patch-544.py'))
    assert patch['UPSTREAM']==PIN
    assert 'wpas_p2p_group_add_persistent' in patch['WRAPPER']
    assert 'P2P-GROUP-STARTED' not in patch['WRAPPER']
    assert 'NULL, NULL, NULL, 0, false, false)' in patch['WRAPPER']
    result=dict(upstream=PIN,version='2.12',required_fix_commits=fixes,
                file_log_option_accepted=True,public_config_parsed=True,
                nonexistent_driver_rejected=True,radio_opened=False,
                installed=False,real_group_verified=False,file_transfer_verified=False)
    with output.open('x') as stream:json.dump(result,stream,indent=2)
    print(json.dumps(result,indent=2))
