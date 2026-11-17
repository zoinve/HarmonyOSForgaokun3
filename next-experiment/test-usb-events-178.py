"""Kernel-message parsing exports fixed fields, never arbitrary text."""
from pathlib import Path
import runpy
import unittest

API = runpy.run_path(str(Path(__file__).with_name('collect-usb-events-178.py')))


class EventTests(unittest.TestCase):
    def test_identity_drops_trailing_private_text(self):
        row = API['parse_event']('usb 3-1.2: New USB device found, idVendor=346d, idProduct=5678, PRIVATE_SERIAL')
        self.assertEqual(row, dict(route='3-1.2', kind='identity', vid='346d', pid='5678'))

    def test_serial_and_product_lines_excluded(self):
        for text in ['usb 3-1: SerialNumber: PRIVATE_SERIAL', 'usb 3-1: Product: PRIVATE_SERIAL']:
            self.assertIsNone(API['parse_event'](text))

    def test_numeric_disconnect_and_errors(self):
        self.assertEqual(API['parse_event']('usb 3-1: USB disconnect, device number 4')['device_number'], 4)
        self.assertEqual(API['parse_event']('usb 3-1: device descriptor read/64, error -71')['errno'], -71)
        self.assertEqual(API['parse_event']('usb 3-1: device not accepting address 4, error -110')['errno'], -110)

    def test_payload_compiles(self):
        compile(API['payload'](), 'remote-178', 'exec')

    def test_usb_connection_speeds(self):
        for speed in ['high-speed','full-speed','SuperSpeed','SuperSpeed Plus','SuperSpeed Plus Gen 2x2']:
            self.assertEqual(API['parse_event']('usb 3-1: new '+speed+' USB device number 4 using xhci-hcd')['kind'], 'connect')


if __name__ == '__main__':
    unittest.main()
