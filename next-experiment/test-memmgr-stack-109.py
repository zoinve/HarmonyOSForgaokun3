"""Admission checks for a bounded original-service diagnostic observer."""
from pathlib import Path
import subprocess
import unittest

BASE = Path(__file__).resolve().parent
SCRIPT = BASE / 'commercial-memmgr-stack-109.sh'


class ObserverTests(unittest.TestCase):
    def setUp(self):
        self.source = SCRIPT.read_text()

    def test_shell_syntax(self):
        subprocess.run(['sh', '-n', str(SCRIPT)], check=True)

    def test_original_probe_pin(self):
        self.assertIn('bc9f14107ebfb682311bf8c714f148df579141bb443a358ff85199cdc443b181', self.source)
        self.assertLess(self.source.index('reason=probe_hash'), self.source.index('/system/bin/timeout 12'))

    def test_bounded_calls(self):
        self.assertIn('seq 1 400', self.source)
        self.assertIn('for phase109 in first later;', self.source)
        self.assertIn('/system/bin/timeout 12 /reference-stack-probe103', self.source)
        self.assertIn('target_not_unique', self.source)
        self.assertIn('target_changed', self.source)

    def test_observe_service_namespace(self):
        self.assertIn('/proc/$pid109/root/dev/memcg', self.source)
        self.assertIn('/proc/$pid109/mountinfo', self.source)
        self.assertIn('success_not_inferred=1', self.source)
        self.assertIn('desktop_not_inferred=1', self.source)

    def test_no_service_or_identity_mutation(self):
        for forbidden in ('setparam', 'param set', 'aa force-stop', 'kill ', 'mount ',
                          'chmod ', 'chown ', 'setuid', 'setcon', 'setenforce', 'reboot',
                          'memory.stat', 'memory.usage_in_bytes'):
            self.assertNotIn(forbidden, self.source)
        self.assertIn('set -C', self.source)


if __name__ == '__main__':
    unittest.main()
