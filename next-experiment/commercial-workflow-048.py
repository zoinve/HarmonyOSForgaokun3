from pathlib import Path
import json
import runpy

b = Path(__file__).resolve().parent
previous = runpy.run_path(str(b / 'commercial-workflow-047.py'))
configure_local_transport = previous['configure_local_transport']


def source048(name):
    text = previous['source047'](name)
    for old, new in [('commercial61-native-047', 'commercial61-native-048'),
                     ('commercial-return-audit-047', 'commercial-return-audit-048'),
                     ('COMMERCIAL047', 'COMMERCIAL048'),
                     ('ordered_chain_equals_full_047', 'ordered_chain_equals_full_048'),
                     ('Matching trace modules 047', 'Trace control boundaries 048')]:
        text = text.replace(old, new)
    if name == 'install-commercial-native':
        manifest = json.loads((b.parent / 'reports/commercial61-native-048/module-provenance.json').read_text())
        assert manifest['all_module_structure_bytes'] == 1216
        assert manifest['dependency_closure_verified'] and manifest['indexes_regenerated']
    return text
