"""Bound the genuine logging command and prevent readiness/identity shortcuts."""
from pathlib import Path
import subprocess
import unittest

SCRIPT = Path(__file__).with_name('commercial-memmgr-dictionary-110.sh')


class DictionaryTests(unittest.TestCase):
    def setUp(self):
        self.source = SCRIPT.read_text()

    def test_shell(self):
        subprocess.run(['sh', '-n', str(SCRIPT)], check=True)

    def test_original_generator_only_once(self):
        command = '/system/bin/timeout 15 /system/bin/hilog -d /system/lib64/libmemmgrservice.z.so'
        self.assertEqual(self.source.count(command), 1)
        self.assertLess(self.source.index('reason=cli_hash'), self.source.index(command))
        self.assertLess(self.source.index('reason=service_elf_hash'), self.source.index(command))

    def test_actual_dictionary_and_output_required(self):
        self.assertIn('success_not_inferred=1', self.source)
        self.assertIn('DICT110_EXPECTED_FILE_PRESENT value=0', self.source)
        self.assertIn('decoded_messages_not_inferred=1', self.source)
        self.assertIn('/data/log/dict/DA/6DFBB4628DCEB0F153CA268C4747DF', self.source)

    def test_bounded_original_queries(self):
        self.assertIn('for phase110 in first later;', self.source)
        self.assertIn('/system/bin/timeout 6 /system/bin/hilog -x -P', self.source)
        self.assertIn('service_changed', self.source)
        self.assertIn('seq 1 400', self.source)

    def test_no_synthetic_state_or_security_changes(self):
        for token in ('param set', 'setparam', 'setenforce', 'aa force-stop', 'kill ',
                      'mount ', 'chmod ', 'chown ', 'memory.stat', 'echo ', 'dd ',
                      'rm ', 'reboot', 'persist.sys.hilog'):
            self.assertNotIn(token, self.source)
        self.assertIn('set -C', self.source)
        self.assertIn('desktop_not_inferred=1', self.source)


if __name__ == '__main__':
    unittest.main()
