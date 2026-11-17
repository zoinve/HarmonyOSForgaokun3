"""Resolve original module imports and inspect its external config wrapper."""
from pathlib import Path

base = Path(__file__).resolve().parent
source = (base / 'audit-commercial-dock-flow-086.py').read_text()
anchor = "'/DefaultLayoutConfig&1.0.0;', '/LayoutConfigManager&1.0.0;')"
assert source.count(anchor) == 1
source = source.replace(anchor,
    "'/DefaultLayoutConfig&1.0.0;', '/LayoutConfigManager&1.0.0;', "
    "'/GetLayoutInfoFromConfig&1.0.0;', '/ConfigParseUtil&1.0.0;')", 1)
source = source.replace('commercial-dock-flow-audit-086', 'commercial-config-wrapper-audit-087')
anchor = '    assert decoded\n'
addition = '''    module_imports = []
    for entry in records:
        field = next((f for f in entry['fields'] if f['name'] == 'moduleRecordIdx'), None)
        if field is None:
            continue
        _, cursor = parser.read_uleb128(data, field['offset'] + 8, len(data))
        assert data[cursor] == 2
        offset = struct.unpack_from('<I', data, cursor + 1)[0]
        literal_count, request_count = struct.unpack_from('<II', data, offset)
        assert request_count < 1024
        cursor = offset + 8
        requests = []
        for _ in range(request_count):
            string_offset = struct.unpack_from('<I', data, cursor)[0]
            requests.append(parser.read_string_item(data, string_offset, len(data)))
            cursor += 4
        count = struct.unpack_from('<I', data, cursor)[0]
        assert count < 1024
        cursor += 4
        imports = []
        for index in range(count):
            local, imported, request = struct.unpack_from('<IIH', data, cursor)
            cursor += 10
            assert request < len(requests)
            imports.append(dict(index=index, local=parser.read_string_item(data, local, len(data)),
                                imported=parser.read_string_item(data, imported, len(data)),
                                request=requests[request]))
        module_imports.append(dict(record=entry['record']['name'], module_offset=offset,
                                   literal_count=literal_count, requests=requests, regular_imports=imports))
'''
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + addition, 1)
anchor = "    for name, blob in resources.items():"
assert source.count(anchor) == 1
source = source.replace(anchor,
    "    with (folder / 'module-imports.json').open('x') as stream:\n        json.dump(module_imports, stream, indent=2)\n" + anchor, 1)
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
