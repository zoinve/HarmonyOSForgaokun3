"""Exercise bounded observer paths using an isolated synthetic filesystem."""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest

BASE = Path(__file__).resolve().parent
SOURCE = (BASE/'commercial-server-stack-104.sh').read_text()


class ObserverTests(unittest.TestCase):
    def scenario(self, guide='6684', server='930', probe_status=0, bad_hash=False, prior_log=False):
        with tempfile.TemporaryDirectory(prefix='server104-test-') as temp:
            root = Path(temp)
            (root/'data').mkdir()
            (root/'proc/930/task/1455').mkdir(parents=True)
            (root/'proc/uptime').write_text('70.00 0.00\n')
            for kind, body in [('comm', 'IPC_1'), ('wchan', 'futex_wait_queue'), ('syscall', '98 0 0')]:
                (root/'proc/930/task/1455'/kind).write_text(body)
            tools = root/'tools'
            tools.mkdir()
            contents = {
                'sha256sum': "#!/bin/sh\nprintf '%s  %s\\n' '"+('bad' if bad_hash else 'bc9f14107ebfb682311bf8c714f148df579141bb443a358ff85199cdc443b181')+"' '"+str(root/'reference-stack-probe103')+"'\n",
                'pidof': '''#!/bin/sh
case "$1" in
com.huawei.hmos.hwstartupguide) printf '%s' "$GUIDE";;
CollaborationFwk) printf '%s' "$SERVER";;
com.ohos.sceneboard) printf 4575;;
esac
''',
                'sleep': '''#!/bin/sh
printf 'sleep %s\\n' "$1" >> "$CALLS"
''',
                'timeout': '''#!/bin/sh
printf 'timeout %s\\n' "$*" >> "$CALLS"
shift
exec "$@"
''',
            }
            for name, body in contents.items():
                (tools/name).write_text(body)
                (tools/name).chmod(0o755)
            for name in ('cat', 'seq'):
                (tools/name).symlink_to('/usr/bin/'+name)
            probe = root/'reference-stack-probe103'
            probe.write_text('''#!/bin/sh
printf 'dump %s\\n' "$*" >> "$CALLS"
printf 'APP_STACK_RESULT pid=%s result=%s\\n' "$1" "$RESULT"
exit "$RESULT"
''')
            probe.chmod(0o755)
            path = root/'observer.sh'
            path.write_text(SOURCE.replace('/system/bin/', str(tools)+'/')
                            .replace('/data/', str(root/'data')+'/')
                            .replace('/proc/', str(root/'proc')+'/')
                            .replace('/reference-stack-probe103', str(probe)))
            log = root/'data/commercial-server-stack104.log'
            if prior_log:
                log.write_text('prior evidence\n')
            calls = root/'calls'
            env = dict(os.environ, GUIDE=guide, SERVER=server, RESULT=str(probe_status), CALLS=str(calls))
            run = subprocess.run(['/bin/sh', str(path)], env=env, capture_output=True, timeout=5)
            return run.returncode, log.read_text(), calls.read_text() if calls.exists() else ''

    def test_single_capture_and_task_evidence(self):
        status, log, calls = self.scenario()
        self.assertEqual(status, 0)
        self.assertIn('SERVER104_TASK tid=1455', log)
        self.assertIn('futex_wait_queue', log)
        self.assertIn('same_pid=1', log)
        self.assertEqual(calls.count('dump 930 all'), 1)
        self.assertIn('sleep 5\n', calls)
        self.assertIn('timeout 12 ', calls)

    def test_refuse_wrong_hash(self):
        status, log, calls = self.scenario(bad_hash=True)
        self.assertEqual(status, 1)
        self.assertIn('reason=probe_hash', log)
        self.assertNotIn('dump ', calls)

    def test_no_guide_is_bounded(self):
        status, log, calls = self.scenario(guide='')
        self.assertEqual(status, 1)
        self.assertIn('reason=guide_not_unique', log)
        self.assertEqual(calls.count('sleep 1\n'), 120)
        self.assertNotIn('dump ', calls)

    def test_refuse_ambiguous_pids(self):
        for kwargs in [dict(guide='6684 6685'), dict(server='930 931'), dict(server='1')]:
            status, log, calls = self.scenario(**kwargs)
            self.assertEqual(status, 1)
            self.assertIn('SERVER104_REFUSED', log)
            self.assertNotIn('dump ', calls)

    def test_capture_failure_is_not_success(self):
        status, log, calls = self.scenario(probe_status=2)
        self.assertEqual(status, 0)
        self.assertIn('SERVER104_CAPTURE_END status=2 success_not_inferred=1', log)
        self.assertEqual(calls.count('dump 930 all'), 1)

    def test_prior_log_not_overwritten(self):
        status, log, calls = self.scenario(prior_log=True)
        self.assertNotEqual(status, 0)
        self.assertEqual(log, 'prior evidence\n')
        self.assertEqual(calls, '')


if __name__ == '__main__':
    unittest.main()
