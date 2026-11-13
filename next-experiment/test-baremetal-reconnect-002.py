"""Exercise immediate reconnect admission without rebooting or contacting a host."""
from pathlib import Path
import runpy
import time
import unittest


class Reconnect(unittest.TestCase):
    def setUp(self):
        self.wait = runpy.run_path(str(Path(__file__).with_name('baremetal-reconnect-002.py')))['wait_for_return']
        self.old = '11111111-1111-4111-8111-111111111111'
        self.new = dict(boot_id='22222222-2222-4222-8222-222222222222',
                        kernel='7.1.0-rc3-gaokun3+', cmdline='root=UUID=example')

    def test_first_probe_has_no_initial_delay(self):
        # An initial fixed sleep would exhaust this deadline before probing.
        result = self.wait(self.old, lambda: self.new, timeout=0.1, interval=1)
        self.assertEqual(result['returned']['boot_id'], self.new['boot_id'])
        self.assertLess(result['attempts'][0]['started_seconds'], 0.1)

    def test_old_session_and_diagnostic_are_not_returned_ubuntu(self):
        states = iter([dict(self.new, boot_id=self.old),
                       dict(self.new, cmdline='harmony.diag=1'), None, self.new])
        result = self.wait(self.old, lambda: next(states), timeout=1, interval=0.001)
        self.assertEqual(result['returned'], self.new)
        self.assertEqual(len(result['attempts']), 4)

    def test_invalid_boot_identity_is_refused(self):
        states = iter([dict(self.new, boot_id='not-a-boot-id'),
                       dict(self.new, kernel=''), self.new])
        result = self.wait(self.old, lambda: next(states), timeout=1, interval=0.001)
        self.assertEqual(len(result['attempts']), 3)

    def test_timeout_never_claims_old_session_returned(self):
        start = time.monotonic()
        result = self.wait(self.old, lambda: dict(self.new, boot_id=self.old),
                           timeout=0.03, interval=0.005)
        self.assertIsNone(result['returned'])
        self.assertTrue(result['timed_out'])
        self.assertLess(time.monotonic() - start, 1)


if __name__ == '__main__':
    unittest.main()
