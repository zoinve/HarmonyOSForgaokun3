"""Offline gates for one virtual-hardware-variable workload comparison."""
from pathlib import Path
import runpy
import unittest

HERE = Path(__file__).parent


class DisplayLoadTests(unittest.TestCase):
    def test_only_virtual_resolution_changes_in_fresh_run(self):
        p = HERE / 'run-baremetal-sdk-original-init-099.py'
        self.assertTrue(p.exists(), 'missing fresh lower-pixel-load runner')
        s = runpy.run_path(str(p))['payload']
        compile(s, '099-run-offline', 'exec')
        self.assertIn("'virtio-gpu-device,xres=800,yres=600'", s)
        self.assertIn('baremetal-sdk-original-init-098/result.json', s)
        self.assertNotIn('baremetal-sdk-original-init-099/result.json', s)
        self.assertIn('GRAPHICS098_', s)
        self.assertNotIn('GRAPHICS099_', s)
        self.assertIn('original-init-qemu-099', s)
        self.assertIn('harmony-sdk-qemu099-', s)
        self.assertIn('original-graphics-provider-005', s)
        self.assertIn('original-graphics-egl-009', s)
        self.assertIn('(120,360,480,540,570,600,620,640,650,660)', s.replace(' ', ''))
        self.assertNotIn('ssh ', s)

    def test_verifier_keeps_guest_bytes_and_full_artifact_checks(self):
        p = HERE / 'verify-original-graphics-boot-099.py'
        self.assertTrue(p.exists(), 'missing independent workload-comparison verifier')
        ns = runpy.run_path(str(p))
        s = ns['source']
        compile(s, '099-verification-offline', 'exec')
        self.assertIn("number='099', tag='098'", s)
        self.assertIn("result['initrd_sha256'] == baseline['initrd_sha256']", s)
        self.assertIn('original_images_independent_hashes', s)
        self.assertIn('independent_artifacts=json.loads(checked.stdout)', s)
        self.assertIn('physical_board_test=False', s)
        self.assertIn('unchanged_guest_initrd_verified', s)
        self.assertEqual(s.count('baremetal-sdk-original-init-qemu-098'), 1)
        raw = (b'GRAPHICS098_POWER_SERVICE_QUERY sample=41 pid=666 original_tool=1 tail=400\n'
               b'actual failure\nGRAPHICS098_POWER_SERVICE_QUERY_END sample=41 pid=666 status=14')
        self.assertEqual(ns['parse_power_service'](raw)[0]['wait_status'], 14)

    def test_inherited_device_gate_accepts_only_the_requested_device_properties(self):
        s = runpy.run_path(str(HERE / 'verify-original-graphics-boot-099.py'))['source']
        self.assertEqual(s.count("'virtio-gpu-device' in command"), 0)
        self.assertIn("'virtio-gpu-device,xres=800,yres=600' in command", s)


if __name__ == '__main__':
    unittest.main()
