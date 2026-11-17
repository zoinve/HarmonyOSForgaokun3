"""Synthetic parser fixtures only, not target graphics acceptance."""
from pathlib import Path
import runpy,unittest
b=Path(__file__).resolve().parent
assert (b/'commercial-scanout-017.py').is_file(),'missing strict actual-frame decoder'
decode=runpy.run_path(str(b/'commercial-scanout-017.py'))['decode']
class Scanout(unittest.TestCase):
    def test_exact_rgb_frame(self):
        blob=b'P6\n2 1\n255\n'+bytes([255,0,0,0,255,0])
        result=decode(len(blob),blob.hex())
        self.assertEqual((result['width'],result['height']),(2,1))
        self.assertEqual(result['unique_rgb_colors'],2)
        self.assertEqual(result['blob'],blob)
    def test_truncation_and_untrusted_dimensions(self):
        for blob in [b'P6\n160 256\n255\n',b'P6\n9999999 1\n255\nx',b'P3\n1 1\n255\nxxx']:
            with self.assertRaises(ValueError):decode(len(blob),blob.hex())
        with self.assertRaises(ValueError):decode(20,'00')
if __name__=='__main__':unittest.main()
