from pathlib import Path
import runpy
import unittest

PARSER = runpy.run_path(str(Path(__file__).with_name('analyze-server-stack-104.py')))['stack_blocks']


class ParserTests(unittest.TestCase):
    def test_multiple_threads_and_code_offsets(self):
        body = b'Tid:930, Name:main\n#00 pc 0000af /system/lib64/liba.so\nTid:1455, Name:IPC\n#00 pc 000001 /system/lib64/libb.so\n'
        blocks = PARSER(body, lambda b: b.decode())
        self.assertEqual(len(blocks), 2)
        self.assertEqual(blocks[0]['frames'][0]['code_offset'], 175)
        self.assertEqual(blocks[1]['frames'][0]['code_offset'], 1)
        self.assertEqual(blocks[1]['frames'][0]['line'], 4)

    def test_frames_without_thread_header_are_not_attributed(self):
        self.assertEqual(PARSER(b'#00 pc 1234 /system/lib64/liba.so\n', lambda b: b.decode()), [])

    def test_malformed_frame_is_not_accepted(self):
        blocks = PARSER(b'Tid:930\n#00 pc NOTHEX /system/lib64/liba.so\n', lambda b: b.decode())
        self.assertEqual(blocks[0]['frames'], [])


if __name__ == '__main__':
    unittest.main()
