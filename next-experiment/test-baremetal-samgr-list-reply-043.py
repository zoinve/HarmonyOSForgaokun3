"""Reject malformed/truncated SA replies rather than interpreting transport success as readiness."""
from pathlib import Path
import runpy
import unittest


class Reply(unittest.TestCase):
    def setUp(self):
        path=Path(__file__).with_name('baremetal-samgr-list-reply-043.py')
        self.assertTrue(path.exists(),'bounded SA reply decoder is not implemented')
        self.decode=runpy.run_path(str(path))['decode_list_reply']
        # status=0, count=2, UTF16 strings "10" and "200", each null-terminated/aligned.
        self.valid=bytes.fromhex('0000000002000000020000003100300000000000030000003200300030000000')

    def test_decodes_complete_vector(self):
        self.assertEqual(self.decode(self.valid),['10','200'])
        self.assertEqual(self.decode(bytes(8)),[])

    def test_policy_error_is_not_an_empty_success(self):
        with self.assertRaisesRegex(ValueError,'status=-1'):
            self.decode(bytes.fromhex('ffffffff00000000'))

    def test_rejects_truncation_counts_lengths_and_termination(self):
        malformed=[self.valid[:n] for n in range(len(self.valid))]
        malformed += [bytes.fromhex('00000000ffffffff'),bytes.fromhex('0000000001100000'),
                      self.valid[:8]+bytes.fromhex('ffffff7f')+self.valid[12:],
                      self.valid[:16]+b'\x01\x00'+self.valid[18:],self.valid+b'\x00']
        for data in malformed:
            with self.subTest(data=data.hex()),self.assertRaises(ValueError):
                self.decode(data)


if __name__=='__main__':
    unittest.main()
