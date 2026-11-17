"""Offline script-scope and executable guard checks; not desktop evidence."""
from pathlib import Path
import hashlib
import json
import runpy
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
API = runpy.run_path(str(Path(__file__).with_name('oobe-single-launch-114.py')))
REFERENCE = ROOT / 'reports/commercial61-native-099/reference-original.sh'
ORIGINAL = REFERENCE.read_text()
ADAPTED = API['adapt'](ORIGINAL)


class SingleLaunch(unittest.TestCase):
    def test_exact_change_scope(self):
        self.assertEqual(ADAPTED.replace(API['GUARD'], API['LAUNCH'], 1), ORIGINAL)

    def test_no_duplicate_start(self):
        self.assertNotIn('/system/bin/aa start ', ADAPTED)
        self.assertEqual(ADAPTED.count('/system/bin/aa force-stop '), 1)
        self.assertIn('sleep 10', ADAPTED)

    def test_missing_scene_fails_closed(self):
        result = subprocess.run(['/bin/sh', '-c', 'pidof() { return 1; };\n' + API['GUARD']],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn('NO_SECOND_START', result.stdout)

    def test_existing_scene_handoff(self):
        result = subprocess.run(['/bin/sh', '-c', 'pidof() { echo 123; return 0; };\n' + API['GUARD']],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('NO_SECOND_START', result.stdout)

    def test_shell_syntax(self):
        result = subprocess.run(['/bin/sh', '-n'], input=ADAPTED, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_ambiguous_source_rejected(self):
        with self.assertRaises(AssertionError):
            API['adapt'](ORIGINAL + API['LAUNCH'] + '\n')


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(SingleLaunch)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    assert result.wasSuccessful()
    output = ROOT / 'reports/oobe-single-launch-114'
    assert not output.exists(), 'Preserve numbered evidence'
    output.mkdir()
    (output / 'reference-adapted.sh').open('x').write(ADAPTED)
    metadata = dict(tests_run=result.testsRun, all_passed=True,
                    reference_sha256=hashlib.sha256(ORIGINAL.encode()).hexdigest(),
                    adapted_sha256=hashlib.sha256(ADAPTED.encode()).hexdigest(),
                    sole_change='Replace second SceneBoard aa start with existing-process guard',
                    early_launch_and_account_bridge_must_remain=True,
                    original_guide_recovery_unchanged=True, force_stop_calls=1,
                    installed=False, target_boot_performed=False, desktop_verified=False)
    (output / 'result.json').open('x').write(json.dumps(metadata, indent=2))
