"""Archive public rendering-mode source and actual commercial property code."""
from pathlib import Path
import hashlib
import json
import subprocess
import urllib.request

BASE = Path(__file__).resolve().parents[1]
COMMIT = '0fa4396a14a9717472a45ca45f184338760f720a'
PATHS = [
    'rosen/modules/render_service_base/include/platform/common/rs_system_properties.h',
    'rosen/modules/render_service/core/pipeline/main_thread/rs_uni_render_visitor.cpp',
]


def main():
    out = BASE / 'reports/commercial-partial-render-audit-059'
    assert not out.exists(), 'Preserve numbered audit evidence'
    bodies = []
    for path in PATHS:
        url = 'https://raw.githubusercontent.com/openharmony/graphic_graphic_2d/' + COMMIT + '/' + path
        with urllib.request.urlopen(url, timeout=30) as response:
            assert response.status == 200
            data = response.read()
        bodies.append((path, url, data))
    header = bodies[0][2].decode()
    assert 'DISABLED = 0' in header and 'SET_DAMAGE_BUT_COMPLETE_RENDER' in header
    visitor = bodies[1][2].decode()
    assert 'GetUniPartialRenderEnabled()' in visitor
    binaries = {
        'base': ('40bd0307b161f0f46ea82d3b08e3dca7819a5c4492066f0e462b8e172e2c50c8', '0x692c2c', '0x692e10'),
        'service': ('009cb202aa11d9cb51af3b045c404038ee231883949a132ced8ea2fbaa52b654', '0x3678e0', '0x367b00'),
    }
    assembly = {}
    for name, (sha, start, end) in binaries.items():
        binary = BASE / 'reports/commercial-oneway-audit-045' / (name + '.so')
        assert hashlib.sha256(binary.read_bytes()).hexdigest() == sha
        assembly[name] = subprocess.check_output([
            'llvm-objdump-19', '-d', '--demangle', '--start-address=' + start,
            '--stop-address=' + end, str(binary)], text=True)
    assert 'ConvertToInt' in assembly['base'] and 'CachedParameterCreate' in assembly['base']
    assert 'cmp\tw0, #0x0' in assembly['service'] and 'cmp\tw9, #0x1' in assembly['service']
    out.mkdir()
    files = []
    for path, url, data in bodies:
        name = Path(path).name
        (out / name).open('xb').write(data)
        files.append(dict(path=name, upstream_path=path, url=url, bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
    for name, text in assembly.items():
        (out / (name + '-partial-render.asm')).open('x').write(text)
    result = dict(commit=COMMIT, files=files, supporting_source_only=True,
                  commercial_binary_identity_claimed=False,
                  original_binary_hashes_verified=True,
                  original_public_parameter='rosen.uni.partialrender.enabled',
                  selected_value=0, source_mode='DISABLED',
                  original_integer_reader_default=4,
                  runtime_configuration_not_yet_tested=True,
                  actual_desktop_verified=False)
    (out / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
