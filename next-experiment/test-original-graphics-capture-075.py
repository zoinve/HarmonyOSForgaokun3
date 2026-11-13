"""Offline tests for observation-only virtual scanout capture."""
from pathlib import Path
import runpy
import struct
import unittest
import zlib

HERE = Path(__file__).parent


class VirtualCapture(unittest.TestCase):
    def test_ppm_pixels_are_preserved_in_png(self):
        path = HERE / 'original-graphics-qmp-capture-001.py'
        self.assertTrue(path.exists(), 'missing virtual scanout capture helper')
        module = runpy.run_path(str(path))
        result = module['decode_ppm'](b'P6\n2 1\n255\n' + bytes([255, 0, 0, 0, 0, 255]))
        self.assertEqual(result, (2, 1, bytes([255, 0, 0, 0, 0, 255])))
        png = module['encode_png'](*result)
        self.assertTrue(png.startswith(b'\x89PNG\r\n\x1a\n'))
        size = struct.unpack('!I', png[33:37])[0]
        self.assertEqual(png[37:41], b'IDAT')
        self.assertEqual(zlib.decompress(png[41:41 + size]), b'\0' + result[2])
        with self.assertRaises(ValueError):
            module['decode_ppm'](b'P6\n2 1\n255\n\x00')

    def test_runner_reuses_verified_guest_and_observes_only(self):
        path = HERE / 'run-baremetal-sdk-original-init-075.py'
        self.assertTrue(path.exists(), 'missing virtual scanout runner')
        payload = runpy.run_path(str(path))['payload']
        for text in ('original-init-qemu-075', 'original-init-074/result.json',
                     'GRAPHICS074_', 'original-graphics-provider-004',
                     'original-graphics-egl-009', 'readonly=on',
                     'virtio-mmio.force-legacy=false', 'query-status', 'screendump'):
            self.assertIn(text, payload)
        self.assertNotIn('system_reset', payload)
        self.assertIn('wait=off', payload)
        compile(payload, 'offline-virtual-capture-075', 'exec')

    def test_qmp_has_a_total_deadline_not_only_per_message_timeouts(self):
        source = (HERE / 'original-graphics-qmp-capture-001.py').read_text()
        self.assertIn('deadline = time.monotonic() + 12', source)
        self.assertIn('deadline - time.monotonic()', source)

    def test_independent_frame_check_rejects_altered_pixels(self):
        path = HERE / 'verify-original-graphics-boot-075.py'
        self.assertTrue(path.exists(), 'missing independent scanout verification')
        module = runpy.run_path(str(path))
        helper = runpy.run_path(str(HERE / 'original-graphics-qmp-capture-001.py'))
        ppm = b'P6\n2 1\n255\n' + bytes([255, 0, 0, 0, 0, 255])
        png = helper['encode_png'](2, 1, ppm[-6:])
        result = module['inspect_frame'](ppm, png)
        self.assertEqual((result['width'], result['height']), (2, 1))
        self.assertEqual(result['nonblack_pixels'], 2)
        with self.assertRaises(AssertionError):
            module['inspect_frame'](ppm[:-1] + b'\0', png)
        self.assertIn("number='075', tag='074'", module['source'])
        compile(module['source'], 'offline-scanout-verifier-075', 'exec')


if __name__ == '__main__':
    unittest.main()
