"""Exercise the actual commercial HiLog unsigned domain gate, not a permissive sink."""
from pathlib import Path
import runpy, unittest

base=Path(__file__).resolve().parent

def commercial_core_domain(domain):
    # Original libhilog.so 0x15b24..0x15b30: add w8,domain,0xf2f00000;
    # cmn w8,0x100000; b.cs accepted. Both operations use 32-bit arithmetic.
    return ((domain+0xf2f00000)&0xffffffff)+0x100000 >= 0x100000000

class Domain(unittest.TestCase):
    def test_original_domain_is_rejected_and_new_header_is_accepted(self):
        old=runpy.run_path(str(base/'commercial-egl-trace-025.py'))['HEADER']
        self.assertFalse(commercial_core_domain(0xD02510))
        self.assertIn('0xD02510',old)
        path=base/'commercial-egl-trace-026.py'
        self.assertTrue(path.exists(),'missing corrected diagnostic domain')
        new=runpy.run_path(str(path))['HEADER']
        self.assertTrue(commercial_core_domain(0x0D002510))
        self.assertEqual(new,old.replace('025','026').replace('0xD02610','0x0D002510'))
        for d in [0x0D000000,0x0D0FFFFF]:self.assertTrue(commercial_core_domain(d))
        for d in [0x0CFFFFFF,0x0D100000,0,0xffffffff]:self.assertFalse(commercial_core_domain(d))

if __name__=='__main__':unittest.main()
