from pathlib import Path
import copy
import json
import runpy
import unittest

BASE = Path(__file__).resolve().parent
repair = runpy.run_path(str(BASE / 'commercial-config-sandbox-088.py'))['repair']


class ConfigView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads((BASE.parent / 'reports/commercial61-native-088/original-appdata-sandbox.json').read_text())

    def test_exact_single_scene_mount(self):
        before = copy.deepcopy(self.original)
        after = repair(before)
        scene = next(g['com.ohos.sceneboard'][0] for g in after['individual'] if 'com.ohos.sceneboard' in g)
        alias = scene['mount-paths'].pop()
        self.assertEqual(alias, {'src-path': '/system/etc', 'sandbox-path': '/usr/system/etc',
                                'sandbox-flags': ['bind', 'rec'], 'check-action-status': 'true'})
        self.assertEqual(after, before)
        self.assertEqual(before, self.original)

    def test_conflicting_mount_refused(self):
        modified = repair(self.original)
        with self.assertRaises(AssertionError):
            repair(modified)

    def test_missing_already_visible_config_refused(self):
        modified = copy.deepcopy(self.original)
        base = modified['common'][0]['app-base'][0]
        base['mount-paths'] = [m for m in base['mount-paths'] if m.get('sandbox-path') != '/system/etc']
        with self.assertRaises(AssertionError):
            repair(modified)

    def test_disabled_sandbox_refused(self):
        modified = copy.deepcopy(self.original)
        modified['common'][0]['top-sandbox-switch'] = 'OFF'
        with self.assertRaises(AssertionError):
            repair(modified)

    def test_original_library_alias_required(self):
        modified = copy.deepcopy(self.original)
        base = modified['common'][0]['app-base'][0]
        base['mount-paths'] = [m for m in base['mount-paths'] if m.get('sandbox-path') != '/usr/system/lib64']
        with self.assertRaises(AssertionError):
            repair(modified)

    def test_conflicting_canonical_symlink_refused(self):
        modified = copy.deepcopy(self.original)
        scene = next(g['com.ohos.sceneboard'][0] for g in modified['individual'] if 'com.ohos.sceneboard' in g)
        scene['symbol-links'].append({'link-name': '/usr/system', 'target-name': '/system'})
        with self.assertRaises(AssertionError):
            repair(modified)


if __name__ == '__main__':
    unittest.main()
