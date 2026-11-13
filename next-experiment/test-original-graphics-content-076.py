"""Real Commit results and passive process evidence; no fabricated frames."""
from pathlib import Path
import runpy
import unittest

HERE = Path(__file__).parent
REFERENCE = Path('C:/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports/graphics/composer.cpp')


class ContentObservation(unittest.TestCase):
    def test_commit_trace_is_reversible_and_returns_real_result(self):
        path = HERE / 'original-composer-trace-003.py'
        self.assertTrue(path.exists(), 'missing real Commit return trace')
        module = runpy.run_path(str(path))
        original = REFERENCE.read_text()
        traced = module['adapt'](original)
        self.assertEqual(module['strip_trace'](traced), original)
        self.assertEqual(traced.count('return composer_trace_result_003(('), 7)
        self.assertIn('errno = saved;', traced)
        self.assertIn('return result;', traced)
        self.assertNotIn('eglGetError(', traced)

    def test_new_provider_uses_trace_without_original_service_changes(self):
        path = HERE / 'build-original-graphics-provider-005.py'
        self.assertTrue(path.exists(), 'missing Commit-observation provider')
        payload = runpy.run_path(str(path))['payload']
        self.assertIn('original-composer-trace-003.py', payload)
        self.assertIn('original-graphics-provider-005', payload)
        self.assertIn('--no-undefined', payload)
        compile(payload, 'offline-content-provider-005', 'exec')

    def test_passive_process_snapshot_and_virtual_capture_keep_isolation(self):
        fixture = HERE / 'prepare-baremetal-sdk-original-init-076.py'
        runner = HERE / 'run-baremetal-sdk-original-init-076.py'
        self.assertTrue(fixture.exists(), 'missing all-process content observer')
        self.assertTrue(runner.exists(), 'missing content capture runner')
        source = runpy.run_path(str(fixture))['source']
        self.assertIn('GRAPHICS076_ALL_PROCESS', source)
        self.assertIn('all_process_count++ < 256', source)
        self.assertNotIn('setuid(', source)
        self.assertNotIn('setcon(', source)
        payload = runpy.run_path(str(runner))['payload']
        for text in ('original-init-qemu-076', 'original-init-076/result.json',
                     'original-graphics-provider-005', 'original-graphics-egl-009',
                     'readonly=on', 'screendump', 'graphics-ashmem.ko'):
            self.assertIn(text, payload)
        compile(payload, 'offline-content-runner-076', 'exec')

    def test_verifier_reports_real_returns_without_desktop_claim(self):
        verifier = HERE / 'verify-original-graphics-boot-076.py'
        self.assertTrue(verifier.exists(), 'missing content verification')
        module = runpy.run_path(str(verifier))
        self.assertEqual(module['decode_commit_result']('Commit_rc_0'), 0)
        self.assertEqual(module['decode_commit_result']('Commit_rc_neg_1'), -1)
        self.assertIsNone(module['decode_commit_result']('entry_Commit'))
        raw = b'GRAPHICS076_STATE sample=17 pid=42 field=composer_remote bytes=8 errno=0 base=0x1000 value=0x1234 private_hash_specific_state=1\n'
        self.assertEqual(module['parse_state_records'](raw)[0]['value'], 0x1234)
        self.assertIn('observed_all_processes', module['source'])
        self.assertIn('actual_commit_return_records', module['source'])
        self.assertNotIn("assert result['initrd_sha256']==", module['source'])
        compile(module['source'], 'offline-content-verifier-076', 'exec')


if __name__ == '__main__':
    unittest.main()
