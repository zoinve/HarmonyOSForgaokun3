"""Exercise the real FIFO/grep trigger against isolated synthetic logs."""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest

BASE = Path(__file__).resolve().parent
SOURCE = (BASE / 'commercial-server-stack-107.sh').read_text()
QUERY = '11-15 23:53:42.302  4878  4878 I C04613/com.ohos.sceneboard/CFWKProxy: [device_picker_client.cpp:388]GetTrustedDeviceListWithAbilityFilter# start\n'


class ObserverTests(unittest.TestCase):
    def scenario(self, text=QUERY, server='936', dm='733', scene='4878', bad_hash=False, prior_log=False, probe_status=0):
        with tempfile.TemporaryDirectory(prefix='server107-test-') as temp:
            root = Path(temp)
            (root / 'data').mkdir()
            (root / 'proc').mkdir()
            (root / 'proc/uptime').write_text('67.00 0.00\n')
            tools = root / 'tools'
            tools.mkdir()
            for name in ('cat', 'seq', 'mkfifo', 'grep', 'rm', 'sh'):
                (tools / name).symlink_to('/usr/bin/' + name)
            # Use an actual timeout with a shorter test-only trigger bound.
            (tools / 'timeout').write_text('#!/bin/sh\nshift\nexec /usr/bin/timeout 2 "$@"\n')
            (tools / 'sleep').write_text('#!/bin/sh\nexit 0\n')
            (tools / 'pidof').write_text('''#!/bin/sh
case "$1" in
com.ohos.sceneboard) printf '%s' "$SCENE";;
device_manager) printf '%s' "$DM";;
CollaborationFwk) printf '%s' "$SERVER";;
esac
''')
            probe = root / 'reference-stack-probe103'
            digest = 'bad' if bad_hash else 'bc9f14107ebfb682311bf8c714f148df579141bb443a358ff85199cdc443b181'
            (tools / 'sha256sum').write_text("#!/bin/sh\nprintf '%s  %s\\n' '" + digest + "' '" + str(probe) + "'\n")
            (root / 'input.log').write_text(text)
            (tools / 'hilog').write_text('#!/bin/sh\nexec /usr/bin/cat "$INPUT"\n')
            for tool in tools.iterdir():
                if not tool.is_symlink():
                    tool.chmod(0o755)
            probe.write_text('''#!/bin/sh
printf 'dump %s\n' "$*" >> "$CALLS"
printf 'APP_STACK_RESULT pid=%s result=%s\n' "$1" "$RESULT"
exit "$RESULT"
''')
            probe.chmod(0o755)
            script = root / 'observer.sh'
            script.write_text(SOURCE.replace('/system/bin/', str(tools) + '/')
                              .replace('/data/', str(root / 'data') + '/')
                              .replace('/proc/', str(root / 'proc') + '/')
                              .replace('/reference-stack-probe103', str(probe)))
            log = root / 'data/commercial-server-stack107.log'
            if prior_log:
                log.write_text('prior evidence\n')
            calls = root / 'calls'
            env = dict(os.environ, SCENE=scene, DM=dm, SERVER=server, RESULT=str(probe_status),
                       CALLS=str(calls), INPUT=str(root / 'input.log'))
            run = subprocess.run(['/bin/sh', str(script)], capture_output=True, env=env, timeout=5)
            return run.returncode, log.read_text(), calls.read_text() if calls.exists() else '', (root / 'data/commercial-query107.fifo').exists()

    def test_trigger_and_order(self):
        status, log, calls, fifo = self.scenario()
        self.assertEqual(status, 0)
        self.assertEqual(calls, 'dump 733 all\ndump 936 all\n')
        self.assertLess(log.index('SERVER107_QUERY_EVENT'), log.index('SERVER107_DFX_CALL_BEGIN'))
        self.assertFalse(fifo)

    def test_other_scene_not_trigger(self):
        status, log, calls, fifo = self.scenario(text=QUERY.replace('4878', '9999'))
        self.assertEqual(status, 1)
        self.assertIn('reason=query_event_missing', log)
        self.assertEqual(calls, '')
        self.assertFalse(fifo)

    def test_query_end_not_trigger(self):
        status, log, calls, fifo = self.scenario(text=QUERY.replace('# start', '# end'))
        self.assertEqual(status, 1)
        self.assertEqual(calls, '')
        self.assertFalse(fifo)

    def test_wrong_hash_refused(self):
        status, log, calls, fifo = self.scenario(bad_hash=True)
        self.assertEqual(status, 1)
        self.assertIn('reason=probe_hash', log)
        self.assertEqual(calls, '')

    def test_ambiguous_target_refused(self):
        for options in (dict(dm='733 734'), dict(server=''), dict(dm='1'), dict(scene='4878 4879')):
            status, log, calls, fifo = self.scenario(**options)
            self.assertEqual(status, 1)
            self.assertIn('SERVER107_REFUSED', log)
            self.assertEqual(calls, '')
            self.assertFalse(fifo)

    def test_native_failure_not_hidden(self):
        status, log, calls, fifo = self.scenario(probe_status=2)
        self.assertEqual(status, 0)
        self.assertEqual(log.count('status=2 success_not_inferred=1'), 2)
        self.assertEqual(calls.count('dump '), 2)

    def test_previous_evidence_preserved(self):
        status, log, calls, fifo = self.scenario(prior_log=True)
        self.assertNotEqual(status, 0)
        self.assertEqual(log, 'prior evidence\n')
        self.assertEqual(calls, '')


if __name__ == '__main__':
    unittest.main()
