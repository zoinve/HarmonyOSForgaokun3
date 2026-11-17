"""Build a separate P2P-only supplicant; never install packages or touch radios."""
from pathlib import Path
import hashlib
import io
import json
import os
import runpy
import shutil
import subprocess
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
BUILD = Path('/home/zoinve/harmony-virgl-883')
SOURCE = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/hostap-share-reference-495')
PACKAGES = {
    'libnl-3-dev_3.7.0-2_amd64.deb': 'a33e1f6c8f04f621c3604b98880e84d2a7d50da57fe15107ed3006c8ed9085ef',
    'libnl-genl-3-dev_3.7.0-2_amd64.deb': '96cff16b1346c12d494c42727ca516fe80e3f4ca5e22c34b6eb8d83f04e4aa4e',
}


if __name__ == '__main__':
    patch = runpy.run_path(str(ROOT / 'next-experiment/share-supplicant-patch-497.py'))
    assert subprocess.check_output(['git', '-C', str(SOURCE), 'rev-parse', 'HEAD'], text=True).strip() == patch['UPSTREAM']
    work = BUILD / 'share-supplicant-499'
    report = ROOT / 'reports/share-supplicant-499'
    assert not work.exists() and not report.exists()
    work.mkdir()
    report.mkdir()
    headers = work / 'headers'
    for name, digest in PACKAGES.items():
        data = urllib.request.urlopen('https://deb.debian.org/debian/pool/main/libn/libnl3/' + name, timeout=30).read()
        assert hashlib.sha256(data).hexdigest() == digest
        archive = work / name
        archive.open('xb').write(data)
        subprocess.run(['dpkg-deb', '-x', str(archive), str(headers)], check=True)
    archive = subprocess.check_output(['git', '-C', str(SOURCE), 'archive',
                                       patch['UPSTREAM'], 'src', 'wpa_supplicant'])
    with tarfile.open(fileobj=io.BytesIO(archive), mode='r:') as source:
        source.extractall(work, filter='data')
    control = work / 'wpa_supplicant/ctrl_iface.c'
    control.write_text(patch['control'](control.read_text()))
    driver = work / 'src/drivers/driver_nl80211.c'
    driver.write_text(patch['driver'](driver.read_text()))
    shutil.copyfile(ROOT / 'next-experiment/share-magiclink-497.h', work / 'wpa_supplicant/share-magiclink-497.h')
    libraries = work / 'link'
    libraries.mkdir()
    original = BUILD / 'native-wpa-083/usr/lib/aarch64-linux-gnu'
    record = json.loads((BUILD / 'native-wpa-083/result.json').read_text())
    for name in ['libnl-3', 'libnl-genl-3']:
        library = original / (name + '.so.200')
        expected, = [row for row in record['files'] if row['path'].endswith('/' + library.name)]
        assert hashlib.sha256(library.read_bytes()).hexdigest() == expected['sha256']
        (libraries / (name + '.so')).symlink_to(library)
    config = '''CONFIG_DRIVER_NL80211=y
CONFIG_LIBNL32=y
CONFIG_CTRL_IFACE=y
CONFIG_BACKEND=file
CONFIG_P2P=y
CONFIG_WPS=y
CONFIG_AP=y
CONFIG_TLS=internal
CONFIG_CRYPTO=internal
CONFIG_INTERNAL_LIBTOMMATH=y
CONFIG_INTERNAL_LIBTOMMATH_FAST=y
CONFIG_NO_CONFIG_WRITE=y
CONFIG_NO_CONFIG_BLOBS=y
CONFIG_IEEE80211W=y
'''
    config += 'CFLAGS += -I' + str(headers / 'usr/include/libnl3') + '\n'
    config += 'LIBS += -L' + str(libraries) + '\n'
    (work / 'wpa_supplicant/.config').open('x').write(config)
    env = dict(os.environ, CC='aarch64-linux-gnu-gcc', PKG_CONFIG='/bin/false')
    with (report / 'build.log').open('xb') as log:
        result = subprocess.run(['make', '-C', str(work / 'wpa_supplicant'), '-j4', 'wpa_supplicant'],
                                env=env, stdout=log, stderr=subprocess.STDOUT, timeout=900)
    assert result.returncode == 0, result.returncode
    binary = work / 'wpa_supplicant/wpa_supplicant'
    subprocess.run(['aarch64-linux-gnu-strip', str(binary)], check=True)
    data = binary.read_bytes()
    assert data[:4] == b'\x7fELF' and int.from_bytes(data[18:20], 'little') == 183
    dynamic = subprocess.check_output(['aarch64-linux-gnu-readelf', '-d', str(binary)], text=True)
    (report / 'dynamic.txt').open('x').write(dynamic)
    result = dict(upstream=patch['UPSTREAM'], binary=str(binary), bytes=len(data),
        sha256=hashlib.sha256(data).hexdigest(), p2p_only=True,
        normal_wlan_supplicant_replaced=False, original_ohos_bridge_unmodified=True,
        real_upstream_wpa_handshake_required=True, synthetic_connection_events=False,
        installed=False, runtime_verified=False, huawei_share_transfer_verified=False)
    (report / 'result.json').open('x').write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
