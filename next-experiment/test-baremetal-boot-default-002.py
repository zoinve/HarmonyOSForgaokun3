"""Exercise the production default guard with real EFI-format scratch files."""
from pathlib import Path
import ast
import json
import runpy
import tempfile
import unittest
import sys

base = Path(__file__).resolve().parent
candidate = '--candidate-002' in sys.argv
if candidate: sys.argv.remove('--candidate-002')

class DefaultGuard(unittest.TestCase):
    def guard(self, persistent, effective):
        path = base / ('start-baremetal-diagnostic-trial-002.py' if candidate else
                       'start-baremetal-diagnostic-trial-001.py')
        self.assertTrue(path.exists(), 'Versioned persistent-default fix is missing')
        namespace = runpy.run_path(str(path), run_name='guard_test_no_execution')
        payload = namespace['payload']
        guards = [node for node in ast.walk(ast.parse(payload)) if isinstance(node, ast.Assert)
                  and '8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
                  in ast.get_source_segment(payload, node)]
        self.assertEqual(len(guards), 1)
        with tempfile.TemporaryDirectory() as scratch:
            var = Path(scratch)
            guid = '4a67b082-0a4c-41cf-b6c7-440b29bb8c4f'
            (var / ('LoaderEntryDefault-' + guid)).write_bytes(
                b'\x07\x00\x00\x00' + (persistent + '\0').encode('utf-16-le'))
            values = dict(var=var, guid=guid,
                          entries=[dict(id=effective, isDefault=True)])
            return eval(compile(ast.Expression(guards[0].test), '<actual-production-guard>', 'eval'), values)

    def test_one_shot_effective_default_does_not_replace_persistent_default(self):
        audit = json.loads((base.parent / 'reports/baremetal-diagnostic-trial-001-guard-audit.json').read_text())
        self.assertTrue(self.guard(audit['persistent_default'], audit['effective_defaults'][0]))

    def test_changed_persistent_default_is_refused_even_if_listing_says_ubuntu(self):
        self.assertFalse(self.guard('harmony-native-diag-004.conf',
            '8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'))

if __name__ == '__main__': unittest.main()
