"""Read-only decoder regression checks; no device operations."""
import json
from pathlib import Path
import runpy
import unittest
import yaml

MOD = runpy.run_path(str(Path(__file__).with_name('decode-commercial-oobe-methods-079.py')))
OUT = MOD['OUT']
TABLE = MOD['instruction_table'](yaml.safe_load((OUT / 'openharmony-isa-1e0c629.yaml').read_bytes()))


class DecoderTests(unittest.TestCase):
    def test_string_signature_without_instruction_property(self):
        result = MOD['decode'](bytes.fromhex('3e000065'), TABLE, ['original log'])
        self.assertEqual(result[0]['operands'][0]['string'], 'original log')

    def test_valid_branch(self):
        self.assertEqual(MOD['decode'](bytes.fromhex('4d0265'), TABLE, [])[0]['target'], 2)

    def test_reject_branch_into_operand(self):
        with self.assertRaises(AssertionError):
            MOD['decode'](bytes.fromhex('4d0165'), TABLE, [])

    def test_reject_truncated_operand(self):
        with self.assertRaises(AssertionError):
            MOD['decode'](bytes.fromhex('4200'), TABLE, [])

    def test_reject_truncated_prefix(self):
        with self.assertRaises(AssertionError):
            MOD['decode'](bytes.fromhex('fd'), TABLE, [])

    def test_reject_out_of_range_string(self):
        with self.assertRaises(AssertionError):
            MOD['decode'](bytes.fromhex('3e0100'), TABLE, ['only zero'])

    def test_real_artifact_consistency(self):
        result = json.loads((OUT / 'decoded-methods-revision2.json').read_text())
        self.assertEqual(len(result['methods']), 123)
        self.assertEqual(sum(len(m['instructions']) for m in result['methods']), 5924)
        for method in result['methods']:
            instructions = method['instructions']
            self.assertEqual(sum(len(bytes.fromhex(i['raw'])) for i in instructions), method['method']['code_size'])
            boundaries = {i['offset'] for i in instructions}
            self.assertTrue(all(i['target'] in boundaries for i in instructions if 'target' in i))


if __name__ == '__main__':
    unittest.main()
