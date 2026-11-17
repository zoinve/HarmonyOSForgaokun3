"""Only a path alias may change; existing sandbox grants must remain exact."""
from pathlib import Path
import copy, runpy, unittest

module = Path(__file__).with_name('commercial-sandbox-008.py')
assert module.is_file(), 'missing sandbox path-alias repair'
repair = runpy.run_path(str(module))['repair']

class SandboxAliasTests(unittest.TestCase):
    def baseline(self):
        return {'sandbox-root': '/mnt/sandbox/system',
                'mount-bind-paths': [{'src-path': '/system/profile', 'sandbox-path': '/system/profile',
                                      'sandbox-flags': ['bind', 'rec', 'private']}],
                'mount-bind-files': [{'src-path': '/vendor/example', 'sandbox-path': '/system/example'}],
                'symbol-links': [{'target-name': '/system/bin', 'link-name': '/bin'}]}

    def test_only_alias_added_and_input_unchanged(self):
        old = self.baseline(); before = copy.deepcopy(old); new = repair(old)
        self.assertEqual(old, before)
        self.assertEqual(new['symbol-links'][-1], {'target-name': '/system', 'link-name': '/usr/system'})
        new['symbol-links'].pop()
        self.assertEqual(new, old)

    def test_reject_unexposed_profile_or_existing_usr_alias(self):
        old = self.baseline(); old['mount-bind-paths'] = []
        with self.assertRaises(AssertionError): repair(old)
        old = self.baseline(); old['symbol-links'].append({'target-name': '/', 'link-name': '/usr'})
        with self.assertRaises(AssertionError): repair(old)

    def test_refuse_reapply(self):
        with self.assertRaises(AssertionError): repair(repair(self.baseline()))

if __name__ == '__main__': unittest.main()
