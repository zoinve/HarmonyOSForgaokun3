from pathlib import Path
import runpy
import unittest

module = runpy.run_path(str(Path(__file__).with_name('analyze-commercial-artifacts-086.py')))


def phase(mode, body=b'', status=0, net=22):
    return (f'PHASE_BEGIN wifi-supplicant-{mode}086\nNETWORK084_TARGET_CONTEXT pid=11 net_inode={net} mnt_inode=33 pid_inode=44 root_verified=1 mode={mode} connectivity_not_inferred=1\n'.encode() +
            body + f'PHASE_END wifi-supplicant-{mode}086 status={status}\n'.encode())


def file(body=b'Native stack\n', count=None):
    size = len(body) if count is None else count
    return (f'EVENT086_FILE_BEGIN name=THREAD_BLOCK_3S-42-20261115.log size={size}\n'.encode() + body +
            f'\nEVENT086_FILE_END name=THREAD_BLOCK_3S-42-20261115.log bytes={size} eof=1 errno=0 full_file_not_inferred=1\n'.encode())


class ArtifactTests(unittest.TestCase):
    def test_exact_event_bytes_recovered(self):
        result = module['event_files'](phase('start') + phase('events', file()))
        self.assertEqual(result['files'][0]['body'], b'Native stack\n')
        self.assertFalse(result['rejected'])

    def test_mismatched_byte_count_refused(self):
        result = module['event_files'](phase('start') + phase('events', file(count=1)))
        self.assertFalse(result['files'])
        self.assertEqual(len(result['rejected']), 1)

    def test_wrong_context_and_failed_phase_refused(self):
        for candidate in (phase('events', file(), net=99), phase('events', file(), status=124)):
            self.assertFalse(module['event_files'](phase('start') + candidate)['files'])

    def test_duplicate_snapshots_not_duplicate_files(self):
        result = module['event_files'](phase('start') + phase('events', file()) * 2)
        self.assertEqual(len(result['files']), 1)

    def test_incomplete_phase_not_admitted(self):
        body = phase('events', file()).split(b'PHASE_END')[0]
        self.assertFalse(module['event_files'](phase('start') + body)['files'])

    def test_original_json_attributes_parsed_structurally(self):
        data = {'attributes': {'type': 'Root'}, 'children': [{'attributes': {'text': 'Next', 'bounds': '[1,2][3,4]', 'clickable': 'true'}}]}
        nodes = module['layout_nodes'](data)
        self.assertEqual(len(nodes), 2)
        self.assertEqual(nodes[1]['text'], 'Next')

    def test_excessively_deep_layout_refused(self):
        data = {}
        for _ in range(130):
            data = {'children': [data]}
        with self.assertRaises(ValueError):
            module['layout_nodes'](data)


if __name__ == '__main__':
    unittest.main()
