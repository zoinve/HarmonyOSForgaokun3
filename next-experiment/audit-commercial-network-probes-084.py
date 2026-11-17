"""Preserve authentic connectivity probe configuration and original curl identity."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
IMAGE = '/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img'


def read(path):
    result = subprocess.run(['debugfs', '-R', 'cat ' + path, IMAGE], capture_output=True, check=True)
    assert result.stdout and b'File not found' not in result.stderr
    return result.stdout


def main():
    folder = ROOT / 'reports/commercial-network-probes-audit-084'
    folder.mkdir(exist_ok=False)
    config = read('/system/etc/netdetectionurl.conf')
    urls = dict(re.findall(r'^([A-Za-z]+ProbeUrl):(https?://\S+)$', config.decode(), re.MULTILINE))
    assert set(urls) == {'HttpProbeUrl', 'HttpsProbeUrl', 'FallbackHttpProbeUrl', 'FallbackHttpsProbeUrl'}
    for value in urls.values():
        parsed = urlsplit(value)
        assert parsed.scheme in ('http', 'https') and parsed.hostname and not parsed.username and not parsed.password
    binary = read('/system/bin/curl')
    with (folder / 'curl').open('xb') as stream:
        stream.write(binary)
    dynamic = subprocess.run(['readelf', '-d', str(folder / 'curl')], capture_output=True, text=True, check=True).stdout
    with (folder / 'netdetectionurl.conf').open('xb') as stream:
        stream.write(config)
    result = dict(config_sha256=hashlib.sha256(config).hexdigest(), original_probe_urls=urls,
                  original_curl_sha256=hashlib.sha256(binary).hexdigest(), original_curl_bytes=len(binary),
                  curl_dynamic_section=dynamic, original_image_written=False,
                  original_binary_executed=False, private_binary_patched=False,
                  connectivity_request_sent=False, dns_or_internet_proven=False)
    with (folder / 'result.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
