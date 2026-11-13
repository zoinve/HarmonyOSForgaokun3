"""Offline streaming archive and fresh candidate-builder gates."""
from pathlib import Path
import hashlib
import io
import runpy
import unittest

HERE = Path(__file__).parent


def archive(rows):
    out = bytearray()
    for number, (name, data) in enumerate(rows + [('TRAILER!!!', b'')], 1):
        name = name.encode() + b'\0'
        values = [number, 0o100755, 0, 0, 1, 0, len(data), 0, 0, 0, 0, len(name), 0]
        out += b'070701' + ''.join(f'{v:08x}' for v in values).encode() + name
        out += b'\0' * ((-len(out)) % 4)
        out += data + b'\0' * ((-len(data)) % 4)
    return bytes(out)


class PackageTests(unittest.TestCase):
    def test_streaming_index_and_bounded_selected_bytes(self):
        path = HERE / 'native-presentation-archive-043.py'
        self.assertTrue(path.exists(), 'missing streaming index')
        scan = runpy.run_path(str(path))['scan_cpio']
        records, selected = scan(io.BytesIO(archive([('init', b'new'), ('large', b'a' * 100000)])), {'init'})
        self.assertEqual(selected, {'init': b'new'})
        self.assertEqual(records['large']['sha256'], hashlib.sha256(b'a' * 100000).hexdigest())
        with self.assertRaises((AssertionError, ValueError, EOFError)):
            scan(io.BytesIO(archive([('init', b'1'), ('init', b'2')])), set())
        with self.assertRaises((AssertionError, ValueError, EOFError)):
            scan(io.BytesIO(archive([('init', b'abc')])[:120]), set())

    def test_new_builder_retains_baseline_and_original_security(self):
        path = HERE / 'build-native-original-graphics-boot-043.py'
        self.assertTrue(path.exists(), 'missing fresh native candidate builder')
        ns = runpy.run_path(str(path))
        source = ns['payload']
        compile(source, 'native043-package-offline', 'exec')
        self.assertIn("root/'native-presentation-043'", source)
        self.assertIn('native-original-graphics-boot-043', source)
        self.assertIn('scan_cpio', source)
        self.assertIn('scratch_reused_from_base032', source)
        self.assertIn('original_service_credentials_unmodified=True', source)
        self.assertIn('original_images_readonly=True', source)
        self.assertIn('automatic_input_injection=False', source)
        self.assertIn('native_boot_attempted=False', source)
        self.assertNotIn('ssh ', source)

    def test_independent_audit_reads_real_archives_without_execution(self):
        path = HERE / 'verify-native-presentation-package-043.py'
        self.assertTrue(path.exists(), 'missing independent candidate audit')
        payload = runpy.run_path(str(path))['payload']
        compile(payload, 'native043-independent-package-offline', 'exec')
        self.assertIn("gzip.open(path,'rb')", payload)
        self.assertIn('expected_outer', payload)
        self.assertIn('original_images_independent_hashes=True', payload)
        self.assertIn('device_accessed=False', payload)
        self.assertIn('installed=False', payload)
        self.assertNotIn('ssh ', payload)


if __name__ == '__main__':
    unittest.main()
