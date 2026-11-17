"""Constrain the metadata collector's axis ABI and no-event-read contract."""
from pathlib import Path
import ast
import runpy
import unittest

PAYLOAD = runpy.run_path(str(Path(__file__).with_name('collect-input-usb-147.py')))['PAYLOAD']


class MetadataTests(unittest.TestCase):
    def test_payload_compiles(self):
        compile(PAYLOAD, '<remote>', 'exec')

    def test_no_event_read_or_write(self):
        tree = ast.parse(PAYLOAD)
        forbidden = {'write', 'write_bytes', 'write_text', 'system', 'popen', 'readv', 'readinto'}
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                self.assertNotIn(node.func.attr, forbidden)
                self.assertFalse(isinstance(node.func.value, ast.Name) and node.func.value.id == 'os' and node.func.attr == 'read')

    def test_axis_query_abi_and_no_values_exported(self):
        import fcntl
        import os
        import struct
        from unittest.mock import patch
        tree = ast.parse(PAYLOAD)
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'axes')
        namespace = dict(os=os, fcntl=fcntl, struct=struct, errno=__import__('errno'), sys=__import__('sys'))
        exec(compile(ast.Module(body=[function], type_ignores=[]), '<axes>', 'exec'), namespace)
        with patch.object(os, 'open', return_value=9), patch.object(os, 'close') as close:
            with patch.object(fcntl, 'ioctl', side_effect=[(1 << 53).to_bytes(8, 'little'), struct.pack('6i', 1234, 0, 2559, 0, 0, 10)]) as ioctl:
                result = namespace['axes']('/dev/input/event99')
        self.assertEqual(result['53']['maximum'], 2559)
        self.assertNotIn('value', result['53'])
        self.assertEqual(set(result), {'53'})
        self.assertEqual(ioctl.call_args_list[1].args[1], 0x80184575)
        close.assert_called_once_with(9)


if __name__ == '__main__':
    unittest.main()
