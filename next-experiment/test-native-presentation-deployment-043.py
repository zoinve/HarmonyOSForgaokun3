"""Offline source gates; never run a historical or remote operational script."""
from pathlib import Path
import runpy
import unittest

HERE = Path(__file__).parent


class DeploymentTests(unittest.TestCase):
    def test_inventory_is_read_only_and_numbered(self):
        p = HERE / 'audit-native-efi-space-043.py'
        self.assertTrue(p.exists(), 'missing fresh read-only inventory')
        ns = runpy.run_path(str(p))
        text = ns['REMOTE']
        compile(text, '043-inventory', 'exec')
        self.assertIn('efibootmgr', text)
        self.assertIn('file_digest', text)
        self.assertNotIn('.unlink(', text)
        self.assertNotIn('set-oneshot', text)
        self.assertNotIn('reboot', text)

    def test_stage_is_fresh_inert_and_refuses_normal_execution(self):
        p = HERE / 'stage-native-original-graphics-boot-043.py'
        self.assertTrue(p.exists(), 'missing fresh guarded staging')
        ns = runpy.run_path(str(p))
        text = ns['source']
        compile(text, '043-stage', 'exec')
        self.assertIn('native-original-graphics-boot-043', text)
        self.assertIn('r.returncode==77', text)
        self.assertIn('assert not root.exists()', text)
        self.assertNotIn('set-oneshot', text)
        self.assertNotIn('systemctl reboot', text)

    def test_archive_only_consumed_022_and_reject_shared_dependencies(self):
        path = HERE / 'archive-native-consumed-022-for-043.py'
        self.assertTrue(path.exists(), 'missing narrow recoverable retirement')
        ns = runpy.run_path(str(path))
        import json
        data = json.loads((HERE.parent / 'reports/native-presentation-043-efi-inventory.json').read_text())
        plan = ns['retirement_plan'](data)
        self.assertEqual(set(plan), {'loader/entries/native-original-graphics-022+0-1.conf',
                                    'native-original-graphics-022/initrd.img'})
        data['configs']['loader/entries/another.conf'] = 'initrd /native-original-graphics-022/initrd.img\n'
        with self.assertRaises(AssertionError):
            ns['retirement_plan'](data)
        self.assertIn('fsync', ns['REMOTE'])
        self.assertNotIn('rmtree', ns['REMOTE'])

    def test_install_preserves_64mib_and_only_adds_counted_overlay_entry(self):
        path = HERE / 'install-native-presentation-043.py'
        self.assertTrue(path.exists(), 'missing guarded fresh installer')
        ns = runpy.run_path(str(path))
        import json
        retired = json.loads((HERE.parent/'reports/native-presentation-043-efi-archive-022.json').read_text())
        base = retired['configs_after']['loader/entries/native-original-graphics-032.conf']
        text = ns['prepare_entry'](base)
        self.assertEqual(text.count('\ninitrd '), 2)
        self.assertIn('panic=15', text)
        self.assertNotIn('panic=0', text)
        old_options = next(s for s in base.splitlines() if s.startswith('options '))
        self.assertIn(old_options.replace('panic=0', 'panic=15'), text)
        self.assertIn('native-original-graphics-043+1.conf', ns['REMOTE'])
        self.assertIn('64*1024*1024', ns['REMOTE'])
        self.assertNotIn('set-oneshot', ns['REMOTE'])
        self.assertNotIn('systemctl reboot', ns['REMOTE'])
        compile(ns['REMOTE'], 'install-043-offline', 'exec')
        import ast
        constants = [n.value for n in ast.walk(ast.parse(ns['REMOTE']))
                     if isinstance(n, ast.Constant) and isinstance(n.value, str)]
        self.assertTrue(any(v == '\ninitrd ' for v in constants),
                        'remote must check real newlines, not backslash-n text')

    def test_fresh_install_attempt_accepts_actual_artifact_list_not_assumed_map(self):
        path = HERE / 'install-native-presentation-043-attempt-002.py'
        self.assertTrue(path.exists(), 'missing corrected separately numbered attempt')
        ns = runpy.run_path(str(path))
        import json
        candidate = json.loads((HERE.parent/'reports/native-original-graphics-boot-043/result.json').read_text())
        table = ns['artifact_table'](candidate['artifacts'])
        self.assertEqual(len(table), 9)
        self.assertEqual(table['initrd.img']['sha256'],
                         '81e3c9c5a00839d07fd4df55e7989acf31dbed2e4d71b55ccdc452da568eaaed')
        with self.assertRaises(AssertionError):
            ns['artifact_table'](candidate['artifacts'][:-1] + candidate['artifacts'][:1])
        self.assertIn("candidate_artifacts=artifact_table(candidate['artifacts'])", ns['source'])
        compile(ns['source'], 'fresh-install-attempt-002-offline', 'exec')


if __name__ == '__main__':
    unittest.main()
