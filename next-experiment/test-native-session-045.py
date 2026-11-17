"""Offline guards for the user's explicit new address and no-screen-off choice."""
from pathlib import Path
import ast
import runpy
import unittest

HERE = Path(__file__).parent


class SessionTests(unittest.TestCase):
    def policy(self):
        p = HERE / 'native-presentation-session-045.py'
        self.assertTrue(p.exists(), 'missing explicit session policy')
        return runpy.run_path(str(p))

    def test_every_ssh_command_keeps_original_host_key_and_new_address(self):
        p = self.policy()
        s = p['connection_source']("import subprocess\nx=['ssh','matebook','true']\ny=['ssh','-o','ConnectTimeout=3','matebook','true']\n")
        ast.parse(s)
        self.assertIn('10.126.126.14', s)
        self.assertIn('HostKeyAlias=192.168.10.128', s)
        self.assertIn('StrictHostKeyChecking=yes', s)
        self.assertEqual(s.count('[*SSH_BASE,'), 2)
        self.assertNotIn('StrictHostKeyChecking=no', s)

    def test_timer_is_checked_disabled_not_ignored_or_changed(self):
        p = self.policy()
        s = p['timer_guard']("assert cmd(['systemctl','is-active','harmony-lab-screen-off-001.timer']).strip()=='active'\nassert cmd(['systemctl','is-enabled','harmony-lab-screen-off-001.timer']).strip()=='enabled'\n")
        self.assertIn("guard_user_timer_045('is-active','inactive',3)", s)
        self.assertIn("guard_user_timer_045('is-enabled','disabled',1)", s)
        self.assertNotIn('enable --now', s)
        self.assertNotIn('set-property', s)
        compile(s, 'timer-policy-offline', 'exec')

    def test_fresh_deployment_files_do_not_replay_failed_inventory(self):
        for name in ('audit-native-efi-space-045-attempt-002.py',
                     'stage-native-original-graphics-boot-045-attempt-002.py',
                     'install-native-presentation-045-attempt-002.py'):
            path = HERE / name
            self.assertTrue(path.exists(), name)
            s = runpy.run_path(str(path))['source']
            compile(s, name, 'exec')
            self.assertIn('SSH_BASE', s)
            if name.startswith('audit-'):
                self.assertIn('native-presentation-045-efi-inventory-attempt-002.json', s)
            if name.startswith('install-'):
                self.assertIn('64*1024*1024+65536', s)
                self.assertNotIn('set-oneshot', s)

    def test_only_unreferenced_image_can_be_retired_and_old_menu_is_not_restored(self):
        path = HERE / 'archive-native-unreferenced-017-for-045.py'
        self.assertTrue(path.exists(), 'missing strictly scoped retirement')
        p = runpy.run_path(str(path))
        row = dict(path='native-original-graphics-017/initrd.img', bytes=30890833,
                   sha256='7a83f050d595e41a2f70989bd35cc0f70d1cfea986648c7e86ad5a197b04f5db')
        self.assertEqual(p['retirement_plan'](dict(files=[row], configs={})), row)
        with self.assertRaises(AssertionError):
            p['retirement_plan'](dict(files=[row], configs={'x.conf': 'initrd /native-original-graphics-017/initrd.img'}))
        path = HERE / 'install-native-presentation-045-attempt-003.py'
        self.assertTrue(path.exists(), 'missing historical-base installer')
        s = runpy.run_path(str(path))['source']
        self.assertIn('prepare_entry(historical032)', s)
        self.assertNotIn("prepare_entry(inventory['configs']['loader/entries/native-original-graphics-032.conf'])", s)
        self.assertIn('64*1024*1024+65536', s)


if __name__ == '__main__':
    unittest.main()
