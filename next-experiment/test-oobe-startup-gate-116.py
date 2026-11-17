"""Execute event gate with isolated log fixtures; never invoke target services."""
from pathlib import Path
import os
import runpy
import subprocess
import tempfile
import unittest

BASE = Path(__file__).resolve().parent
API = runpy.run_path(str(BASE / 'oobe-startup-gate-116.py'))
SOURCE = (BASE / 'commercial-collaboration-ready-116.sh').read_text()
EVENT = '11-16 01:44:17.500  1080  1661 I C0461C/CollaborationFwk/Detect: [device_detect_service.cpp:949]OnAddSystemAbilityEvent# RegisterHichainProofExceptionStatusCallback, ret: 0'


class Gate(unittest.TestCase):
    def execute(self, event=EVENT, first='1080', second='1080'):
        with tempfile.TemporaryDirectory(prefix='cfwk116-test-') as directory:
            root = Path(directory)
            binary, data = root / 'bin', root / 'data'
            binary.mkdir()
            data.mkdir()
            for command in ('cat', 'seq', 'sleep', 'mkfifo', 'rm', 'timeout', 'grep'):
                (binary / command).symlink_to('/usr/bin/' + command)
            mocks = {
                'hilog': '#!/bin/sh\nprintf "%s\\n" "$MOCK_EVENT"\n',
                'pidof': '#!/bin/sh\nif [ -e "$MOCK_COUNT" ]; then printf "%s\\n" "$MOCK_SECOND"; else : > "$MOCK_COUNT"; printf "%s\\n" "$MOCK_FIRST"; fi\n',
            }
            for name, text in mocks.items():
                path = binary / name
                path.write_text(text)
                path.chmod(0o755)
            adapted = SOURCE.replace('/system/bin/', str(binary) + '/').replace('/data/', str(data) + '/')
            process = subprocess.run(['/bin/sh', '-c', adapted], capture_output=True, text=True, timeout=5,
                env=dict(os.environ, MOCK_EVENT=event, MOCK_FIRST=first, MOCK_SECOND=second,
                         MOCK_COUNT=str(root / 'counter')))
            log = (data / 'commercial-collaboration-ready116.log').read_text()
            self.assertFalse((data / 'commercial-collaboration-ready116.fifo').exists())
            return process.returncode, log

    def test_current_original_event_accepted(self):
        status, log = self.execute()
        self.assertEqual(status, 0)
        self.assertIn('CFWK116_CHECKPOINT_OBSERVED', log)

    def test_other_pid_rejected(self):
        status, log = self.execute(EVENT.replace('  1080 ', '  1081 '))
        self.assertNotEqual(status, 0)
        self.assertNotIn('CFWK116_CHECKPOINT_OBSERVED', log)

    def test_failed_original_callback_rejected(self):
        status, _ = self.execute(EVENT.replace('ret: 0', 'ret: 1'))
        self.assertNotEqual(status, 0)

    def test_other_component_rejected(self):
        status, _ = self.execute(EVENT.replace('CollaborationFwk/Detect', 'other/Detect'))
        self.assertNotEqual(status, 0)

    def test_changed_process_rejected(self):
        status, log = self.execute(second='2000')
        self.assertNotEqual(status, 0)
        self.assertIn('reason=server_changed', log)

    def test_multiple_server_pids_rejected(self):
        status, log = self.execute(first='1080 2000')
        self.assertNotEqual(status, 0)
        self.assertIn('reason=server_not_unique', log)

    def test_patch_preserves_existing_start_and_account_commands(self):
        source = API['ANCHOR'] + '/usr/bin/aa start -b com.ohos.sceneboard\n/usr/bin/begetctl start_service accountmgr\n'
        adapted = API['adapt'](source)
        self.assertEqual(adapted.replace(API['GATE'], '', 1), source)
        self.assertLess(adapted.index('/commercial-collaboration-ready116.sh'), adapted.index('/usr/bin/aa start'))

    def test_shell_syntax(self):
        for source in (SOURCE, API['GATE']):
            result = subprocess.run(['/bin/sh', '-n'], input=source, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
