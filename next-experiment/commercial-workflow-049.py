from pathlib import Path
import json
import runpy

b = Path(__file__).resolve().parent
previous = runpy.run_path(str(b / 'commercial-workflow-048.py'))
configure_local_transport = previous['configure_local_transport']


def source049(name):
    text = previous['source048'](name)
    for old, new in [('commercial61-native-048', 'commercial61-native-049'),
                     ('commercial-return-audit-048', 'commercial-return-audit-049'),
                     ('COMMERCIAL048', 'COMMERCIAL049'),
                     ('ordered_chain_equals_full_048', 'ordered_chain_equals_full_049'),
                     ('Trace control boundaries 048', 'Original service setup stages 049')]:
        text = text.replace(old, new)
    if name == 'install-commercial-native':
        manifest = json.loads((b.parent / 'reports/commercial61-native-049/module-provenance.json').read_text())
        assert manifest['all_module_structure_bytes'] == 1216 and manifest['ashmem_rebuilt']
        assert manifest['dependency_closure_verified'] and manifest['indexes_regenerated']
    return text
