"""Exercise the actual ARM64 option parser, without opening a radio."""
from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BUILD = Path('/home/zoinve/harmony-virgl-883')

def probe(number):
    binary = BUILD / ('share-supplicant-' + str(number)) / 'wpa_supplicant/wpa_supplicant'
    result = subprocess.run(['qemu-aarch64',
        str(BUILD / 'native-wpa-083/lib/ld-linux-aarch64.so.1'), '--library-path',
        str(BUILD / 'native-wpa-083/usr/lib/aarch64-linux-gnu'), str(binary),
        '-f', '/dev/null', '-v'], capture_output=True, text=True, timeout=20)
    text = result.stdout + result.stderr
    return dict(exit_status=result.returncode, version_printed='wpa_supplicant v2.11' in text,
                usage_printed='usage:' in text.lower())

if __name__ == '__main__':
    old = probe(499)
    new = probe(515)
    assert old['exit_status'] == 0 and old['usage_printed'], old
    assert new['exit_status'] == 0 and new['version_printed'] and not new['usage_printed'], new
    result = dict(prior499=old, candidate515=new, radio_opened=False,
                  native_p2p_ready=False, transfer_verified=False)
    output = ROOT / 'reports/share-cli-516.json'
    with output.open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))
