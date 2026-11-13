"""Offline gates for extracting genuine fault reports, without rerunning the VM."""
from pathlib import Path
import runpy
import unittest


class FreezeAuditTests(unittest.TestCase):
    def test_readonly_extraction_pins_this_run_and_preserves_the_source(self):
        p = Path(__file__).with_name('audit-original-render-freeze-097.py')
        self.assertTrue(p.exists(), 'missing original RenderService freeze extractor')
        s = runpy.run_path(str(p))['source']
        compile(s, '097-freeze-extraction-offline', 'exec')
        self.assertIn('baremetal-sdk-original-init-qemu-097/scratch-data.ext4', s)
        self.assertNotIn('baremetal-sdk-original-init-qemu-096', s)
        self.assertIn('sysfreeze-render_service-1003-19700101080856693.log', s)
        self.assertIn('appfreeze-com.ohos.sceneboard-20020034-19700101080834666.log', s)
        self.assertIn('assert hash_guest_file(path) == before', s)
        self.assertIn("'debugfs', '-R', 'cat ' + guest_path", s)
        self.assertNotIn('e2fsck', s)
        self.assertNotIn("'-w'", s)
        self.assertIn(".open('xb')", s)


if __name__ == '__main__':
    unittest.main()
