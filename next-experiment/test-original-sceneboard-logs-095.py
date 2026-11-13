"""Offline checks for original SceneBoard diagnostics, never launch experiments."""
from pathlib import Path
import runpy
import unittest

HERE = Path(__file__).parent


class SceneBoardLogTests(unittest.TestCase):
    def test_real_process_and_original_hilog_without_identity_changes(self):
        p = HERE / 'prepare-baremetal-sdk-original-init-095.py'
        self.assertTrue(p.exists(), 'missing original SceneBoard log fixture')
        ns = runpy.run_path(str(p))
        s = ns['source']
        self.assertIn('graphics_sceneboard_query_095', s)
        self.assertIn('"com.ohos.sceneboard "', s)
        start = s.index('static void graphics_sceneboard_query_095(')
        end = s.index('\nstatic void ', start + 1)
        helper = s[start:end]
        self.assertIn('"/system/bin/hilog", "-z", "400", "-P", argument', helper)
        self.assertIn('alarm(12)', helper)
        self.assertNotIn('setuid(', s)
        self.assertNotIn('setcon(', s)
        self.assertIn('mount("tmpfs", "/mnt", "tmpfs", MS_NOSUID, "mode=0755")', s)
        self.assertIn('mount(NULL, "/mnt", NULL, MS_SLAVE, NULL)', s)
        compile(ns['payload'], '095-build-offline', 'exec')

    def test_new_number_and_full_independent_gates(self):
        for filename in ('run-baremetal-sdk-original-init-095.py', 'verify-original-graphics-boot-095.py'):
            p = HERE / filename
            self.assertTrue(p.exists(), f'missing {filename}')
            ns = runpy.run_path(str(p))
            s = ns.get('payload', ns.get('source'))
            compile(s, filename, 'exec')
            self.assertEqual(s.count('baremetal-sdk-original-init-qemu-094'), 0)
            if filename.startswith('verify-'):
                self.assertIn('original_sceneboard_log_output', s)
                self.assertIn('original_images_independent_hashes', s)
                self.assertIn('independent_artifacts=json.loads(checked.stdout)', s)
                self.assertIn('physical_board_test=False', s)
            else:
                self.assertIn('original-graphics-provider-005', s)
                self.assertIn('original-graphics-egl-009', s)
                self.assertIn('readonly=on', s)


if __name__ == '__main__':
    unittest.main()
