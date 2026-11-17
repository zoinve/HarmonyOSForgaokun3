"""Preserve boot safeguards and pin the matching trace kernel and modules."""
from pathlib import Path
import json
import runpy

b = Path(__file__).resolve().parent
previous = runpy.run_path(str(b / 'commercial-workflow-046.py'))
configure_local_transport = previous['configure_local_transport']


def source047(name):
    text = previous['source046'](name)
    for old, new in [('commercial61-native-046', 'commercial61-native-047'),
                     ('commercial-return-audit-046', 'commercial-return-audit-047'),
                     ('COMMERCIAL046', 'COMMERCIAL047'),
                     ('ordered_chain_equals_full_046', 'ordered_chain_equals_full_047'),
                     ('Original service execution trace 046', 'Matching trace modules 047')]:
        text = text.replace(old, new)
    if name == 'install-commercial-native':
        old = json.loads((b.parent / 'reports/native-trace-kernel-046/result.json').read_text())
        new = json.loads((b.parent / 'reports/native-trace-kernel-047/result.json').read_text())
        modules = json.loads((b.parent / 'reports/commercial61-native-047/module-provenance.json').read_text())
        assert new['previous_unchanged'] and new['configuration_unchanged']
        assert modules['dependency_closure_verified'] and modules['indexes_regenerated']
        assert modules['all_module_structure_bytes'] == 1216 and modules['ashmem_rebuilt']
        text = text.replace('native-original-graphics-046/linux', 'native-original-graphics-047/linux')
        text = text.replace(old['sha256'], new['image_sha256'])
    return text
