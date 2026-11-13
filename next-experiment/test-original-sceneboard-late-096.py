"""Offline gates for cheaper, later original SceneBoard observations."""
from pathlib import Path
import runpy
import unittest

HERE = Path(__file__).parent


class LateSceneBoardTests(unittest.TestCase):
    def test_find_app_before_verbose_filter_without_dumping_its_maps(self):
        p = HERE / 'prepare-baremetal-sdk-original-init-096.py'
        self.assertTrue(p.exists(), 'missing bounded SceneBoard observation fixture')
        ns = runpy.run_path(str(p))
        s = ns['source']
        self.assertLess(s.index('sceneboard_pid = pid;'), s.index('if (!strstr(text,'))
        self.assertNotIn('!strstr(text, "com.ohos.sceneboard")', s)
        self.assertIn('graphics_all_process_076(sample, pid, text);', s)
        self.assertIn('graphics_sceneboard_query_095(sample, sceneboard_pid);', s)
        self.assertIn('"/system/bin/hilog", "-z", "400", "-P", argument', s)
        self.assertNotIn('setuid(', s)
        self.assertIn('mount(NULL, "/mnt", NULL, MS_SLAVE, NULL)', s)
        compile(ns['payload'], '096-build-offline', 'exec')

    def test_fresh_full_verification_and_unchanged_guest_dependencies(self):
        for name in ('run-baremetal-sdk-original-init-096.py', 'verify-original-graphics-boot-096.py'):
            p = HERE / name
            self.assertTrue(p.exists(), f'missing {name}')
            ns = runpy.run_path(str(p))
            s = ns.get('payload', ns.get('source'))
            compile(s, name, 'exec')
            self.assertEqual(s.count('baremetal-sdk-original-init-qemu-095'), 0)
            if name.startswith('run-'):
                self.assertIn('original-graphics-provider-005', s)
                self.assertIn('original-graphics-egl-009', s)
                self.assertIn('readonly=on', s)
            else:
                self.assertIn('original_sceneboard_log_output', s)
                self.assertIn('original_images_independent_hashes', s)
                self.assertIn('independent_artifacts=json.loads(checked.stdout)', s)
                self.assertIn('physical_board_test=False', s)


if __name__ == '__main__':
    unittest.main()
