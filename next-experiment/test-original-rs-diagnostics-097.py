"""Offline gates for bounded original-service log and power-parameter reads."""
from pathlib import Path
import runpy
import unittest

HERE = Path(__file__).parent


class OriginalDiagnostics(unittest.TestCase):
    def test_guarded_original_tools_are_reads_not_security_overrides(self):
        path = HERE / 'prepare-baremetal-sdk-original-init-097.py'
        self.assertTrue(path.exists(), 'missing 097 fixture')
        ns = runpy.run_path(str(path))
        source = ns['source']
        self.assertIn('graphics_render_service_query_097(sample, rs_pid)', source)
        self.assertIn('"/system/bin/hilog", "-z", "400", "-P"', source)
        self.assertIn('"startup.device.ctl", "ohos.startup.powerctrl"', source)
        self.assertIn('"/system/bin/param", "get"', source)
        self.assertIn('sample == 69 || sample == 71', source)
        self.assertNotIn('"/system/bin/param", "set"', source)
        self.assertNotIn('setuid(', source)
        self.assertNotIn('setcon(', source)
        self.assertIn('MS_BIND | MS_REMOUNT | MS_RDONLY | MS_NODEV', source)
        self.assertIn('16777216', source)
        compile(ns['payload'], '097-preparation-offline', 'exec')

    def test_fresh_bounded_scanouts_and_full_independent_checks(self):
        for filename in ('run-baremetal-sdk-original-init-097.py', 'verify-original-graphics-boot-097.py'):
            path = HERE / filename
            self.assertTrue(path.exists(), f'missing {filename}')
            ns = runpy.run_path(str(path))
            source = ns.get('payload', ns.get('source'))
            compile(source, filename, 'exec')
            self.assertEqual(source.count('baremetal-sdk-original-init-qemu-096'), 0)
            if filename.startswith('run-'):
                self.assertIn('(120,360,480,540,570,600,620,640,650,660)', source.replace(' ', ''))
                self.assertIn('original-graphics-provider-005', source)
                self.assertIn('original-graphics-egl-009', source)
                self.assertNotIn('ssh ', source)
            else:
                self.assertIn('original_render_service_log_output', source)
                self.assertIn('original_power_parameter_output', source)
                self.assertIn('original_images_independent_hashes', source)
                self.assertIn('independent_artifacts=json.loads(checked.stdout)', source)
                self.assertIn('physical_board_test=False', source)

    def test_timeout_and_empty_parameter_text_are_not_ready_signals(self):
        path = HERE / 'verify-original-graphics-boot-097.py'
        self.assertTrue(path.exists(), 'missing 097 verifier')
        parser = runpy.run_path(str(path))['parse_diagnostics']
        raw = (b'GRAPHICS097_RS_QUERY sample=61 pid=1289 original_tool=1 tail=400\npartial\n'
               b'GRAPHICS097_RS_QUERY_END sample=61 pid=1289 status=14\n'
               b'GRAPHICS097_POWER_QUERY sample=69 key=startup.device.ctl original_tool=1 read_only=1\n'
               b'GRAPHICS097_POWER_QUERY_END sample=69 key=startup.device.ctl status=0\n')
        result = parser(raw)
        self.assertEqual(result['render_service'][0]['wait_status'], 14)
        self.assertEqual(result['power_parameters'][0]['raw_interleaved_output'], '')


if __name__ == '__main__':
    unittest.main()
