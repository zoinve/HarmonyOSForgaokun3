"""Publication checks never run a device operation or require SDK images."""
import unittest
from verify_source_tree import validate_file


class SourcePolicyTests(unittest.TestCase):
    def test_authored_source_and_markdown_are_allowed(self):
        for name in ['README.md', 'docs/BUILD.md', 'reports/native-render-041.md',
                     'next-experiment/native-gpu-composer-041.h', 'tools/check.py',
                     'next-experiment/commercial-softbus-observer-101.sh',
                     'next-experiment/compat-kernel-489.config']:
            self.assertEqual(validate_file(name, b'# plain text\n'), [])

    def test_images_archives_binaries_and_raw_evidence_are_rejected(self):
        for name in ['system.img', 'install.iso', 'next-experiment/initrd.img',
                     'next-experiment/linux', 'next-experiment/driver.so',
                     'reports/raw.log', 'next-experiment/run-001/runner.py',
                     'references/vendor.c', 'docs/screenshot.png',
                     'next-experiment/private.config']:
            self.assertTrue(validate_file(name, b'text'), name)

    def test_disguised_binary_or_oversized_file_is_rejected(self):
        self.assertTrue(validate_file('next-experiment/probe.c', b'\x7fELF\x00'))
        self.assertTrue(validate_file('docs/test.md', b'a' * (512 * 1024 + 1)))

    def test_credentials_are_rejected_without_printing_them(self):
        private_key = b'-----BEGIN ' + b'OPENSSH PRIVATE KEY-----'
        token = b'ghp_' + b'a' * 36
        for data in [private_key, token]:
            errors = validate_file('docs/test.md', data)
            self.assertTrue(errors)
            self.assertNotIn(data.decode(), ' '.join(errors))


if __name__ == '__main__':
    unittest.main()
