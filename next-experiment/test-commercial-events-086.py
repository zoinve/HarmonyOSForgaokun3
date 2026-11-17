"""Compile the exact consolidated-log reader with bounded mock read effects."""
from pathlib import Path
import importlib.util
import runpy
import unittest

b = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('freeze085', b / 'test-network-freeze-085.py')
parent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parent)
parent.PROBE = runpy.run_path(str(b / 'commercial-network-helper-086.py'))['EVENT']
parent.STUB = parent.STUB.replace('/data/log/eventlog/freeze', '/data/log/eventlog').replace(
    'THREAD_BLOCK_3S_20261115_42_stack', 'THREAD_BLOCK_3S-42-20261115.log')
anchor = 'static int mock_execv(const char *path,char *const args[]){(void)path;(void)args;abort();}'
assert parent.STUB.count(anchor) == 1
parent.STUB = parent.STUB.replace(anchor, '', 1)
anchor = "++reads;memset(buffer,'x',size);return (ssize_t)size;"
assert parent.STUB.count(anchor) == 1
parent.STUB = parent.STUB.replace(anchor, "++reads;if(scenario==6 && reads==1){errno=EINTR;return -1;}if(scenario==7){errno=EIO;return -1;}if(scenario==10)return 0;memset(buffer,'x',size);return (ssize_t)size;", 1)
anchor = 'bytes+=(int)size;return (ssize_t)size;'
assert parent.STUB.count(anchor) == 1
parent.STUB = parent.STUB.replace(anchor, 'if(scenario==9){errno=EIO;return -1;}size_t actual=scenario==8 && size>1 ? size/2 : size;bytes+=(int)actual;return (ssize_t)actual;', 1)
parent.MAIN = parent.MAIN.replace('    if(scenario==99)return network085_probe("https");\n', '').replace('network085_freeze()', 'event086_read()')


class EventTests(parent.FreezeTests):
    def test_files_and_bytes_bounded(self):
        output = self.case(0)
        self.assertIn('rc=0 opened=4 reads=1024 bytes=4194304 enumerated=4 closed=5', output)
        self.assertIn('eof=0 errno=0 full_file_not_inferred=1', output)

    def test_unrelated_files_not_opened_and_enumeration_bounded(self):
        self.assertIn('rc=0 opened=0 reads=0 bytes=0 enumerated=256 closed=1', self.case(5))

    def test_interrupted_read_retried_without_extending_byte_limit(self):
        self.assertIn('rc=0 opened=4 reads=1025 bytes=4194304', self.case(6))

    def test_read_errors_not_reported_as_eof(self):
        output = self.case(7)
        self.assertIn('bytes=0 eof=0 errno=5 full_file_not_inferred=1', output)

    def test_partial_writes_fully_drained(self):
        self.assertIn('rc=0 opened=4 reads=1024 bytes=4194304', self.case(8))

    def test_write_error_recorded(self):
        self.assertIn('bytes=0 eof=0 errno=5 full_file_not_inferred=1', self.case(9))

    def test_actual_eof_separately_reported(self):
        self.assertIn('bytes=0 eof=1 errno=0 full_file_not_inferred=1', self.case(10))


if __name__ == '__main__':
    unittest.main()
