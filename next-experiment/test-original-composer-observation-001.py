"""Offline gates for observing the original composer, not synthesizing screens."""
from pathlib import Path
import ast
import runpy
import unittest

HERE = Path(__file__).parent


class ComposerObservation(unittest.TestCase):
    def test_original_hilog_targets_real_discovered_processes(self):
        path = HERE / 'prepare-baremetal-sdk-original-init-068.py'
        self.assertTrue(path.exists(), 'missing original composer observation fixture')
        source = runpy.run_path(str(path))['source']
        self.assertIn('long composer_pid = 0, manager_pid = 0;', source)
        self.assertIn('long query_pids[] = {rs_pid, composer_pid, manager_pid};', source)
        self.assertIn('"/system/bin/hilog", "-x", "-P", query_pid_arg', source)
        self.assertIn('GRAPHICS068_HDF_HILOG_QUERY', source)
        self.assertNotIn('setuid(', source)
        self.assertNotIn('setcon(', source)
        self.assertIn('enforcing=0', source)

    def test_runner_keeps_existing_providers_and_readonly_images(self):
        path = HERE / 'run-baremetal-sdk-original-init-068.py'
        self.assertTrue(path.exists(), 'missing original composer observation runner')
        payload = runpy.run_path(str(path))['payload']
        ast.parse(payload)
        self.assertIn('original-graphics-egl-009/result.json', payload)
        self.assertIn('original-graphics-provider-002/result.json', payload)
        self.assertIn('format=raw,readonly=on', payload)
        self.assertIn('harmony-sdk-qemu068-', payload)
        self.assertIn('timeout_seconds=360', payload)

    def test_verifier_records_real_hdf_query_outcomes(self):
        path = HERE / 'verify-original-graphics-boot-068.py'
        self.assertTrue(path.exists(), 'missing independent original HDF observation verifier')
        source = runpy.run_path(str(path))['source']
        ast.parse(source)
        self.assertIn('original_hdf_log_queries', source)
        self.assertIn('original_hdf_log_query_results', source)
        self.assertIn('decoded_original_hdf_lines', source)
        self.assertIn('extract_process_pids', source)


if __name__ == '__main__':
    unittest.main()
