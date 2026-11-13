"""Offline safety checks, never launch an operational experiment."""
from pathlib import Path
import runpy
import unittest

HERE = Path(__file__).parent

class QueryTests(unittest.TestCase):
    def test_original_api_query_is_guarded_and_read_only(self):
        p = HERE / 'original-config-query-001.c'
        self.assertTrue(p.exists(), 'missing genuine config API query')
        s = p.read_text()
        for token in ('harmony.original_init_test=1', 'GetCfgFiles', 'FreeCfgFiles',
                      'getuid()', 'diagnostic_caller_not_samgr=1', 'O_RDONLY'):
            self.assertIn(token, s)
        for token in ('setuid(', 'setcon(', 'mkdir(', 'chmod(', 'O_WRONLY', 'SystemWriteParam'):
            self.assertNotIn(token, s)

    def test_scoped_fixture_preserves_original_services(self):
        p = HERE / 'prepare-baremetal-sdk-original-init-083.py'
        self.assertTrue(p.exists(), 'missing scoped fixture')
        source = runpy.run_path(str(p))['source']
        self.assertIn('"/graphics-config-query"', source)
        self.assertNotIn('LD_PRELOAD', source)
        run = HERE / 'run-baremetal-sdk-original-init-083.py'
        self.assertTrue(run.exists(), 'missing immutable numbered runner')
        payload = runpy.run_path(str(run))['payload']
        self.assertIn("add('graphics-config-query'", payload)
        self.assertIn('original-graphics-egl-009', payload)
        compile(payload, '<offline-083-runner>', 'exec')

    def test_verifier_checks_injected_query_and_records_real_results(self):
        p = HERE / 'verify-original-graphics-boot-083.py'
        self.assertTrue(p.exists(), 'missing independent query verification')
        data = runpy.run_path(str(p))
        s = data['source']
        for token in ('config_query_archive_verified=True', 'original_config_query_results',
                      'original_config_query_output', 'physical_board_test=False'):
            self.assertIn(token, s)
        compile(s, '<offline-independent-083>', 'exec')

if __name__ == '__main__':
    unittest.main()
