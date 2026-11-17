from pathlib import Path
import runpy
import unittest

parse = runpy.run_path(str(Path(__file__).with_name('analyze-commercial-config-view-088.py')))['observations']
DIGEST = 'a' * 64
PATH = '/usr/system/etc/hw_launcher_default_workspace.json'


def record(digest=DIGEST, status=0, pid='42'):
    return (f'CONFIG088_PATH_BEGIN pid={pid} path={PATH}\n'
            'CONFIG088_STAT_RESULT status=0\n'
            f'{digest}  /proc/{pid}/root{PATH}\n'
            f'CONFIG088_HASH_RESULT status={status}\n'
            f'CONFIG088_PATH_END pid={pid} path={PATH}\n')


class RuntimePaths(unittest.TestCase):
    def test_exact_success(self):
        self.assertTrue(parse(record(), DIGEST)[0]['expected_file_hash_observed'])

    def test_wrong_hash(self):
        self.assertFalse(parse(record('b' * 64), DIGEST)[0]['expected_file_hash_observed'])

    def test_failed_command(self):
        self.assertFalse(parse(record(status=1), DIGEST)[0]['expected_file_hash_observed'])

    def test_wrong_process_path(self):
        text = record().replace('/proc/42/root', '/proc/43/root')
        self.assertFalse(parse(text, DIGEST)[0]['expected_file_hash_observed'])

    def test_unmatched_footer(self):
        self.assertEqual(parse(record().replace('PATH_END pid=42', 'PATH_END pid=43'), DIGEST), [])

    def test_no_command_result(self):
        text = record().replace('CONFIG088_HASH_RESULT status=0\n', '')
        self.assertFalse(parse(text, DIGEST)[0]['expected_file_hash_observed'])


if __name__ == '__main__':
    unittest.main()
