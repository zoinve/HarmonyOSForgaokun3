"""Read-only inventory of the exact 078 initrd chain and network inputs."""
from pathlib import Path
import gzip
import hashlib
import json
import re
import stat

ROOT = Path(__file__).resolve().parents[1]
BUILD = Path('/home/zoinve/harmony-virgl-883')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def members(data):
    cursor = 0
    while True:
        assert cursor + 110 <= len(data), 'truncated newc header'
        header = data[cursor:cursor + 110]
        assert header[:6] == b'070701', 'unsupported archive format'
        values = [int(header[i:i + 8], 16) for i in range(6, 110, 8)]
        cursor += 110
        name_end = cursor + values[11]
        assert values[11] > 0 and name_end <= len(data)
        assert data[name_end - 1] == 0
        name = data[cursor:name_end - 1].decode()
        cursor = (name_end + 3) & ~3
        end = cursor + values[6]
        assert end <= len(data), 'truncated newc body'
        body = data[cursor:end]
        cursor = (end + 3) & ~3
        if name == 'TRAILER!!!':
            assert not any(data[cursor:]), 'unparsed nonzero archive suffix'
            return
        while name.startswith('./'):
            name = name[2:]
        assert not name.startswith('/') and '..' not in Path(name).parts
        yield name, values[1], body


def main():
    install = json.loads((ROOT / 'reports/commercial61-native-078/installation-result.json').read_text())
    paths = [line.split(' ', 1)[1].lstrip('/') for line in install['entry_text'].splitlines() if line.startswith('initrd ')]
    kernel = json.loads((ROOT / 'reports/native-binder-kernel-045/result.json').read_text())
    config = (BUILD / 'native-binder-kernel-045/out/.config').read_bytes()
    assert sha(config) == kernel['config_sha256']
    assert sha(Path(kernel['image']).read_bytes()) == kernel['sha256']
    merged, archives = {}, []
    relevant = re.compile(r'ath11k|ath\.ko|cfg80211|mac80211|qrtr|mhi|qmi|regulatory|wpa|supplicant|dhcp|/iw$|/ip$|/firmware/|modules\.(dep|alias|softdep)')
    for relative in paths:
        expected_path = ROOT / ('reports/' + relative.split('/')[0] + '/overlay-result.json')
        if relative == 'commercial61-native-016/initrd.img':
            expected = json.loads((ROOT / 'reports/commercial61-native-078/overlay-result.json').read_text())['existing_016_overlay_sha256']
        elif expected_path.exists():
            expected = json.loads(expected_path.read_text())['sha256']
        else:
            manifest = json.loads((ROOT / ('reports/' + relative.split('/')[0] + '/result.json')).read_text())
            expected = next(a['sha256'] for a in manifest['artifacts'] if a['name'] == 'initrd.img')
        directory = relative.split('/')[0]
        candidates = [BUILD / relative, BUILD / directory / 'minimal-overlay.img',
                      BUILD / (directory + '-r2') / 'minimal-overlay.img']
        matching = [p for p in candidates if p.exists() and sha(p.read_bytes()) == expected]
        assert matching, ('no hash-matched deployed archive', relative)
        archive = matching[0]
        packed = archive.read_bytes()
        entries = list(members(gzip.decompress(packed)))
        archives.append(dict(path=relative, local_source=str(archive), sha256=sha(packed), bytes=len(packed), members=len(entries)))
        for name, mode, body in entries:
            if relevant.search(name):
                merged[name] = dict(path=name, mode=mode, bytes=len(body), sha256=sha(body), source=relative,
                                    symlink=body.decode() if stat.S_ISLNK(mode) else None)
    init = (BUILD / 'commercial61-native-078/init.c').read_text()
    result = dict(archives=archives, kernel_sha256=kernel['sha256'], config_sha256=sha(config),
                  kernel_config=[s for s in config.decode().splitlines() if any(n in s for n in (
                      'CONFIG_ATH11K', 'CONFIG_CFG80211', 'CONFIG_MAC80211', 'CONFIG_QRTR', 'CONFIG_MHI',
                      'CONFIG_FW_LOADER', 'CONFIG_USB_RTL8152', 'CONFIG_USB_USBNET'))],
                  network_archive_members=sorted(merged.values(), key=lambda x: x['path']),
                  ath11k_module_members=[n for n in merged if 'ath11k' in n and '.ko' in n],
                  ath11k_firmware_members=[n for n in merged if 'ath11k/' in n and '/firmware/' in '/' + n],
                  explicit_ath11k_load_in_outer='ath11k' in init,
                  original_images_written=False, host_network_changed=False,
                  operational_boot_performed=False, absence_from_initrd_does_not_prove_runtime_absence=True)
    out = ROOT / 'reports/commercial-network-inputs-audit-079'
    out.mkdir(exist_ok=False)
    with (out / 'result.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(dict(archives=len(archives), relevant_members=len(merged),
                         ath11k_modules=result['ath11k_module_members'],
                         ath11k_firmware=result['ath11k_firmware_members'],
                         explicit_ath11k_load=result['explicit_ath11k_load_in_outer'])))


if __name__ == '__main__':
    main()
