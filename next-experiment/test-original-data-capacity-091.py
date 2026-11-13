"""Offline gates for a larger disposable disk, never user or SDK data."""
from pathlib import Path
import runpy
import unittest

HERE = Path(__file__).parent


class DataCapacityTests(unittest.TestCase):
    def test_independent_frame_checks_use_this_trial_not_parent_frames(self):
        source = runpy.run_path(str(HERE / 'verify-original-graphics-boot-091.py'))['source']
        self.assertEqual(source.count('baremetal-sdk-original-init-qemu-090'), 0)
        self.assertIn('baremetal-sdk-original-init-qemu-091', source)
        self.assertIn("sha(p)==sha(q)==row['sha256']", source)

    def test_volume_check_does_not_overwrite_full_artifact_check_result(self):
        source = runpy.run_path(str(HERE / 'verify-original-graphics-boot-091.py'))['source']
        self.assertTrue('volume_checked = subprocess.run' in source,
                        'volume check must retain the independent artifact subprocess result')
        self.assertTrue('independent_artifacts=json.loads(checked.stdout)' in source)
        self.assertTrue('independent_larger_data_volume = json.loads(volume_checked.stdout)' in source)

    def test_guest_requires_exact_larger_volume_and_reports_real_free_space(self):
        path = HERE / 'prepare-baremetal-sdk-original-init-091.py'
        self.assertTrue(path.exists(), 'missing larger-data guest')
        source = runpy.run_path(str(path))['source']
        self.assertIn('"sdk-testdata", 16777216,', source)
        self.assertNotIn('"sdk-testdata", 1048576,', source)
        self.assertIn('statvfs("/data",', source)
        self.assertIn('GRAPHICS091_DATA_CAPACITY', source)
        self.assertIn('MS_BIND | MS_REMOUNT | MS_RDONLY | MS_NODEV', source)
        for forbidden in ('setuid(', 'setcon(', 'SystemWriteParam', 'AUDIT_ADD_RULE'):
            self.assertNotIn(forbidden, source)

    def test_runner_uses_exclusive_lab_disk_and_streamed_verified_retention(self):
        path = HERE / 'run-baremetal-sdk-original-init-091.py'
        self.assertTrue(path.exists(), 'missing larger-data runner')
        payload = runpy.run_path(str(path))['payload']
        self.assertIn('dir=str(work)', payload)
        self.assertIn('scratch.parent==work', payload)
        self.assertIn('17*1024*1024*1024', payload)
        self.assertIn('8*1024*1024*1024', payload)
        self.assertIn('ram_backed=False,disk_backed=True,test_only=True', payload)
        self.assertIn("'--sparse=always'", payload)
        self.assertIn('sha(retained)==after', payload)
        self.assertIn('hashlib.file_digest', payload)
        self.assertIn('original_userdata_attached=False', payload)
        for expected in ('readonly=on', 'original-graphics-provider-005', 'original-graphics-egl-009'):
            self.assertIn(expected, payload)
        self.assertNotIn("dir='/dev/shm'", payload)
        self.assertNotIn('ssh ', payload)
        compile(payload, '<offline-run091>', 'exec')

    def test_verifier_independently_checks_larger_disk_without_assuming_account_success(self):
        path = HERE / 'verify-original-graphics-boot-091.py'
        self.assertTrue(path.exists(), 'missing larger-data verifier')
        data = runpy.run_path(str(path))
        source = data['source']
        for expected in ('independent_larger_data_volume', 'observed_data_capacity',
                         'original_account_log_output', 'config_query_archive_verified=True',
                         'physical_board_test=False', 'hashlib.file_digest'):
            self.assertIn(expected, source)
        rows = data['parse_data_capacity'](b'GRAPHICS091_DATA_CAPACITY sample=24 stat=-1 errno=5 fragment=0 blocks=0 available=0\n')
        self.assertIsNone(rows[0]['available_bytes'])
        rows = data['parse_data_capacity'](b'GRAPHICS091_DATA_CAPACITY sample=30 stat=0 errno=0 fragment=4096 blocks=2000000 available=12345\n')
        self.assertEqual(rows[0]['available_bytes'], 4096 * 12345)
        compile(source, '<offline-verify091>', 'exec')


if __name__ == '__main__':
    unittest.main()
