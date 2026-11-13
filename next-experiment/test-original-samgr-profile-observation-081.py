"""Original SAMGR log/profile visibility, not injected or fabricated SA profiles."""
from pathlib import Path
import runpy
import unittest

HERE = Path(__file__).parent


class OriginalProfiles(unittest.TestCase):
    def test_passive_query_and_process_visible_files(self):
        path = HERE / 'prepare-baremetal-sdk-original-init-081.py'
        self.assertTrue(path.exists(), 'missing original SAMGR observer')
        source = runpy.run_path(str(path))['source']
        self.assertIn('GRAPHICS081_SAMGR_QUERY', source)
        self.assertIn('"/system/bin/hilog", "-a", "600", "-P", argument, NULL', source)
        self.assertIn('/proc/%ld/root/%s/profile/installs.json', source)
        self.assertIn('O_RDONLY | O_CLOEXEC | O_NOFOLLOW', source)
        self.assertNotIn('setuid(', source)
        self.assertNotIn('setcon(', source)
        self.assertNotIn('mkdir("/data/service/el1/public/bms', source)

    def test_runner_and_verifier_keep_full_preservation(self):
        runner = HERE / 'run-baremetal-sdk-original-init-081.py'
        verifier = HERE / 'verify-original-graphics-boot-081.py'
        self.assertTrue(runner.exists(), 'missing isolated SAMGR runner')
        self.assertTrue(verifier.exists(), 'missing independent SAMGR verifier')
        payload = runpy.run_path(str(runner))['payload']
        for text in ('original-init-qemu-081', 'original-init-081/result.json',
                     'readonly=on', 'original-graphics-egl-009', 'original-graphics-provider-005'):
            self.assertIn(text, payload)
        module = runpy.run_path(str(verifier))
        source = module['source']
        self.assertIn('original_samgr_profile_output', source)
        self.assertIn('original_samgr_log_output', source)
        compile(source, 'offline-original-samgr-profile-081', 'exec')
        raw = b'GRAPHICS081_STATE sample=17 pid=42 field=composer_remote bytes=-1 errno=13 base=0x1000 value=0x0 private_hash_specific_state=1\n'
        self.assertIsNone(module['parse_state_records'](raw)[0]['value'])


if __name__ == '__main__':
    unittest.main()
