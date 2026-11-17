"""Reject incomplete or mismatched original memory-service observations."""
from pathlib import Path
import runpy
import unittest

sample_blocks = runpy.run_path(str(Path(__file__).with_name('analyze-original-memmgr-108.py')))['sample_blocks']


class SampleTests(unittest.TestCase):
    prefix = (b'MEMMGR108_SAMPLE_BEGIN target=20\n'
              b'SAMGR_SERVICE id=1909 present=1\n'
              b'MEMMGR108_SA_PROBE status=0 service_success_not_inferred=1\n'
              b'SAMGR_SERVICE_PROBE_PASS\n')

    def test_exact_end(self):
        self.assertTrue(sample_blocks(self.prefix + b'MEMMGR108_SAMPLE_END target=20\n')[0]['genuine_sa_publication_verified'])

    def test_longer_target_is_not_end(self):
        self.assertFalse(sample_blocks(self.prefix + b'MEMMGR108_SAMPLE_END target=200\n')[0]['complete'])

    def test_missing_end(self):
        self.assertFalse(sample_blocks(self.prefix)[0]['genuine_sa_publication_verified'])

    def test_failed_probe(self):
        body = self.prefix.replace(b'status=0 ', b'status=1 ')
        self.assertFalse(sample_blocks(body + b'MEMMGR108_SAMPLE_END target=20\n')[0]['genuine_sa_publication_verified'])


if __name__ == '__main__':
    unittest.main()
