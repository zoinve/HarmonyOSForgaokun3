"""Read original preset literal objects; do not patch ABC or deploy a layout."""
from pathlib import Path
import hashlib
import io
import json
import runpy
import struct
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    folder = ROOT / 'reports/commercial-dock-literals-audit-086-revision4'
    assert not folder.exists()
    parser = runpy.run_path(str(ROOT / 'references/L410-Linux-Compatibility-Platform/abc_record_index.py'))
    image = '/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img'
    hap = subprocess.run(['debugfs', '-R', 'cat /system/app/SceneBoard/SceneBoard.hap', image],
                         capture_output=True, check=True).stdout
    assert hashlib.sha256(hap).hexdigest() == 'f36168b19efc69b6a3246f557ddadd8e0534e5c208c093b6a00e94917391da80'
    archive = zipfile.ZipFile(io.BytesIO(hap))
    data = archive.read('ets/modules.abc')
    manifest = json.loads(archive.read('module.json'))
    audit = json.loads((ROOT / 'reports/commercial-dock-defaults-audit-086-revision3/decoded-methods.json').read_text())
    assert hashlib.sha256(data).hexdigest() == audit['abc_sha256']
    method = next(m for m in audit['methods'] if '/PresetDockItem&' in m['record'])
    header = parser['HEADER'].unpack_from(data)
    regions = [struct.unpack_from('<10I', data, header[13] + i * 40) for i in range(header[12])]
    region = next(r for r in regions if r[0] <= method['method']['offset'] < r[1])

    def literal(index):
        assert 0 <= index < region[4]
        offset = struct.unpack_from('<I', data, region[5] + index * 4)[0]
        count = struct.unpack_from('<I', data, offset)[0]
        assert count % 2 == 0 and count < 512
        cursor, values = offset + 4, []
        for _ in range(count // 2):
            tag = data[cursor]
            cursor += 1
            if tag in (0, 1, 0xff):
                value = data[cursor]
                cursor += 1
                if tag == 1:
                    assert value in (0, 1)
                    value = bool(value)
                elif tag == 0xff:
                    assert value == 0
                    value = None
            elif tag in (2, 5):
                value = struct.unpack_from('<I', data, cursor)[0]
                cursor += 4
                if tag == 5:
                    value = parser['read_string_item'](data, value, len(data))
            elif tag == 4:
                value = struct.unpack_from('<d', data, cursor)[0]
                cursor += 8
            else:
                raise ValueError(f'Unsupported literal tag {tag} at {cursor - 1}')
            values.append(value)
        assert len(values) % 2 == 0
        pairs = list(zip(values[::2], values[1::2]))
        assert all(isinstance(key, str) for key, _ in pairs)
        assert len({key for key, _ in pairs}) == len(pairs)
        return dict(index=index, offset=offset, bytes=cursor-offset,
                    sha256=hashlib.sha256(data[offset:cursor]).hexdigest(), fields=dict(pairs))

    buffers = []
    for insn in method['instructions']:
        if insn['name'] == 'createobjectwithbuffer':
            buffers.append(literal(insn['operands'][-1]['value']))
    result = dict(original_modified=False, operational_boot_performed=False,
                  hap_sha256=hashlib.sha256(hap).hexdigest(), abc_sha256=audit['abc_sha256'],
                  format_reference='arkcompiler_runtime_core/libpandafile/literal_data_accessor-inl.h',
                  module_name=manifest['module']['name'], bundle_name=manifest['app']['bundleName'],
                  abilities=[a['name'] for a in manifest['module'].get('abilities', [])],
                  main_element=manifest['module'].get('mainElement'), literal_objects=buffers,
                  note='Static buffers only; later bytecode assigns constants and nested objects. No candidate is installed.')
    folder.mkdir()
    with (folder / 'result.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
