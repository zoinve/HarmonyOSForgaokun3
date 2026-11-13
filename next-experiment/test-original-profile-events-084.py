"""Offline safety gates; generated operational payloads are never executed here."""
from pathlib import Path
import runpy
import unittest

BASE = Path(__file__).parent


class ProfileEvents(unittest.TestCase):
    def test_guarded_guest_uses_notification_events_not_permission_events(self):
        path = BASE / 'prepare-baremetal-sdk-original-init-084.py'
        self.assertTrue(path.is_file(), 'guest notification observer missing')
        source = runpy.run_path(str(path))['source']
        self.assertIn('fanotify_init(FAN_CLOEXEC | FAN_NONBLOCK', source)
        self.assertIn('FAN_OPEN | FAN_ACCESS | FAN_CLOSE_NOWRITE | FAN_EVENT_ON_CHILD', source)
        self.assertNotIn('FAN_OPEN_PERM', source)
        self.assertNotIn('FAN_ACCESS_PERM', source)
        self.assertNotIn('fanotify_response', source)
        self.assertIn('meta->pid', source)
        self.assertIn('count < 2048', source)
        main = source[source.index('int main('):]
        self.assertLess(main.index('only disk-isolated QEMU virt allowed'),
                        main.index('graphics_profile_events_084();'))
        self.assertLess(main.index('graphics_profile_events_084();'), main.index('execve('))
        runner = runpy.run_path(str(BASE / 'run-baremetal-sdk-original-init-084.py'))['payload']
        compile(runner, 'profile-events-offline', 'exec')
        self.assertIn('format=raw,readonly=on', runner)
        self.assertIn('original-graphics-provider-005', runner)
        self.assertNotIn('ssh', runner)

    def test_verification_keeps_full_hashes_and_actual_samgr_identity(self):
        path = BASE / 'verify-original-graphics-boot-084.py'
        self.assertTrue(path.is_file(), 'independent event verifier missing')
        module = runpy.run_path(str(path))
        source = module['source']
        compile(source, 'verify-profile-events-offline', 'exec')
        self.assertIn('samgr_profile_events', source)
        self.assertIn("5555, 'samgr'", source)
        self.assertIn('config_query_archive_verified=True', source)
        self.assertIn('physical_board_test=False', source)

    def test_event_parser_preserves_pid_mask_path_and_actual_link_error(self):
        path = BASE / 'verify-original-graphics-boot-084.py'
        self.assertTrue(path.is_file(), 'event parser missing')
        parse = runpy.run_path(str(path))['parse_profile_events']
        rows = parse(b'GRAPHICS084_PROFILE_EVENT seq=1 pid=132 mask=0x21 path=/usr/system/profile/installs.json link_errno=0\n'
                     b'GRAPHICS084_PROFILE_EVENT seq=2 pid=900 mask=0x10 path=<readlink_failed> link_errno=2\n')
        self.assertEqual(rows[0], dict(sequence=1, pid=132, mask=33,
                         path_raw='/usr/system/profile/installs.json', link_errno=0))
        self.assertEqual(rows[1]['link_errno'], 2)

    def test_fresh_aarch64_fixture_omits_unavailable_optional_largefile_macro(self):
        path = BASE / 'prepare-baremetal-sdk-original-init-085.py'
        self.assertTrue(path.is_file(), 'fresh compile correction missing')
        source = runpy.run_path(str(path))['source']
        self.assertNotIn('O_LARGEFILE', source)
        self.assertIn('FAN_CLOEXEC | FAN_NONBLOCK, O_RDONLY | O_CLOEXEC', source)
        self.assertIn('FAN_OPEN | FAN_ACCESS | FAN_CLOSE_NOWRITE | FAN_EVENT_ON_CHILD', source)
        runner = runpy.run_path(str(BASE / 'run-baremetal-sdk-original-init-085.py'))['payload']
        compile(runner, 'profile-events-085-offline', 'exec')
        module = runpy.run_path(str(BASE / 'verify-original-graphics-boot-085.py'))
        compile(module['source'], 'verify-profile-events-085-offline', 'exec')
        self.assertEqual(module['parse_profile_events'](
            b'GRAPHICS085_PROFILE_EVENT seq=1 pid=132 mask=0x1 path=/usr/system/profile/installs.json link_errno=0\n'
        )[0]['mask'], 1)


if __name__ == '__main__':
    unittest.main()
