"""Offline gates for reading original power-service decisions, not overriding them."""
from pathlib import Path
import runpy
import unittest

HERE = Path(__file__).parent


class PowerServiceTests(unittest.TestCase):
    def test_original_query_uses_real_pid_without_verbose_mapping_dump(self):
        p = HERE / 'prepare-baremetal-sdk-original-init-098.py'
        self.assertTrue(p.exists(), 'missing power-service observation fixture')
        ns = runpy.run_path(str(p))
        s = ns['source']
        start = s.index('static void graphics_power_service_query_098(')
        end = s.index('\nstatic void ', start + 1)
        helper = s[start:end]
        self.assertIn('"/system/bin/hilog", "-z", "400", "-P", argument', helper)
        self.assertIn('alarm(12)', helper)
        self.assertLess(s.index('powermgr_pid = pid;'), s.index('if (!strstr(text, "render_service")'))
        self.assertNotIn('!strstr(text, "powermgr")', s)
        self.assertNotIn('setuid(', s)
        self.assertIn('MS_BIND | MS_REMOUNT | MS_RDONLY | MS_NODEV', s)
        compile(ns['payload'], '098-offline-prepare', 'exec')

    def test_numbered_run_keeps_original_graph_and_independent_checks(self):
        for name in ('run-baremetal-sdk-original-init-098.py', 'verify-original-graphics-boot-098.py'):
            p = HERE / name
            self.assertTrue(p.exists(), f'missing {name}')
            ns = runpy.run_path(str(p))
            s = ns.get('payload', ns.get('source'))
            compile(s, name, 'exec')
            self.assertEqual(s.count('baremetal-sdk-original-init-qemu-097'), 0)
            if name.startswith('run-'):
                self.assertIn('original-graphics-provider-005', s)
                self.assertIn('original-graphics-egl-009', s)
                self.assertIn('(120,360,480,540,570,600,620,640,650,660)', s)
            else:
                self.assertIn('original_images_independent_hashes', s)
                self.assertIn('independent_artifacts=json.loads(checked.stdout)', s)
                self.assertIn('physical_board_test=False', s)
                self.assertIn('original_power_service_log_output', s)

    def test_timeout_and_business_error_are_preserved_not_readiness(self):
        ns = runpy.run_path(str(HERE / 'verify-original-graphics-boot-098.py'))
        rows = ns['parse_power_service'](
            b'GRAPHICS098_POWER_SERVICE_QUERY sample=41 pid=647 original_tool=1 tail=400\n'
            b'query failed\n'
            b'GRAPHICS098_POWER_SERVICE_QUERY_END sample=41 pid=647 status=14\n')
        self.assertEqual(rows[0]['wait_status'], 14)
        self.assertEqual(rows[0]['raw_interleaved_output'], 'query failed\n')


if __name__ == '__main__':
    unittest.main()
