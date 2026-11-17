"""Admit source generation and exercise USB preflight without target mutation."""
from pathlib import Path
import ast
import json
import runpy
import tempfile
import unittest
from unittest.mock import patch

BASE = Path(__file__).resolve().parent
API = runpy.run_path(str(BASE / 'commercial-workflow-176.py'))


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'sys/class/block').mkdir(parents=True)
        (self.root / 'sys/bus/usb').mkdir(parents=True)
        self.tree = dict(blockdevices=[])

    def disk(self, name='sda', usb=True, size='61849600'):
        parent = self.root / 'sys/devices' / name
        block = parent / 'block' / name
        block.mkdir(parents=True)
        if usb:
            (parent / 'subsystem').symlink_to(self.root / 'sys/bus/usb')
            (parent / 'idVendor').write_text('346d')
            (parent / 'idProduct').write_text('5678')
        for key,value in [('size',size),('removable','1')]:
            (block / key).write_text(value)
        (self.root / 'sys/class/block' / name).symlink_to(block)
        self.tree['blockdevices'].append(dict(name=name,tran='usb',size=31666995200,mountpoints=[None]))

    def preflight(self):
        def mapped(path):
            return self.root / str(path).lstrip('/') if str(path).startswith('/sys/') else Path(path)
        with patch('pathlib.Path', side_effect=mapped), patch('subprocess.check_output', return_value=json.dumps(self.tree)):
            exec(API['USB_PREFLIGHT'], {})

    def test_missing_disk_refused(self):
        with self.assertRaises(AssertionError):self.preflight()

    def test_valid_usb_passes(self):
        self.disk()
        self.preflight()

    def test_nonusb_or_wrong_size_refused(self):
        self.disk(usb=False)
        with self.assertRaises(AssertionError):self.preflight()
        self.disk(name='sdb',size='1')
        with self.assertRaises(AssertionError):self.preflight()

    def test_ambiguity_refused(self):
        self.disk()
        self.disk(name='sdb')
        with self.assertRaises(AssertionError):self.preflight()

    def test_mounted_partition_refused(self):
        self.disk()
        self.tree['blockdevices'][0]['children']=[dict(name='sda1',mountpoints=['/media/usb'])]
        with self.assertRaises(AssertionError):self.preflight()

    def test_preflight_has_no_write_operations(self):
        for forbidden in ['mknod','mount(', 'umount', 'BLKROSET', 'write_text', 'set-oneshot']:
            self.assertNotIn(forbidden, API['USB_PREFLIGHT'].replace('unmount',''))


if __name__ == '__main__':
    report = API['WORKFLOW_REPORT']
    assert not (report / 'workflow-test.json').exists(), 'preserve numbered admission'
    build = json.loads((API['REPORT'] / 'build-test.json').read_text())
    assert build['complete_29_archive_chain_equals_full'] and build['desktop173_runtime_byte_identical']
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(PreflightTests)
    result = unittest.TextTestRunner().run(suite)
    assert result.wasSuccessful() and result.testsRun == 6
    sources = {}
    for operation in API['OPERATIONS']:
        source = API['source176'](operation)
        compile(source, operation, 'exec')
        remote = []
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and '\nfrom pathlib import Path\n' in node.value:
                compile(node.value, operation+'-remote', 'exec')
                remote.append(node.value)
        assert 'StrictHostKeyChecking=yes' in source
        if operation == 'install-commercial-native':
            assert len(remote) == 1
            code = remote[0]
            assert code.index('usb176_preflight()\n') < code.index('root.mkdir()')
            assert code.index('assert estimated176<1800') < code.index('root.mkdir()')
            assert "'initrd /usb176.img'" in code
            assert "sha(dest/'usb176.img')==sha(root/'initrd.img')" in code
            assert "'commercial61-native-176/initrd.img'" in source.split("code='payload='",1)[0]
            assert 'harmony.usb_readonly175=1' in code and '32*1024**2' in code
            assert 'efibootmgr' in code and 'efi_before=before' in code
        elif operation == 'run-commercial-native':
            assert 'attempt_count=1' in source and '+startcode,text=True' in source and '660' in source
            assert '/boot/efi/usb176.img' in source and 'usb176_preflight' in source
        elif operation == 'retrieve-commercial-evidence':
            assert 'ro,noload' in source
            early=json.loads((BASE.parent/'reports/commercial61-native-175-compile-fix-1/early-return-inspection.json').read_text())
            assert early['run'] in source
        sources[operation] = source
    report.mkdir()
    for operation,source in sources.items():
        (report / (operation+'.generated.py')).open('x').write(source)
    result = dict(six_preflight_tests_pass=True,all_generated_sources_compile=True,
        missing_ambiguous_nonusb_wrong_size_and_mounted_disks_refused=True,
        short_alias_hash_checked=True,command_bound_checked_before_install_writes=True,
        authenticated_single_boot_and_preservation_guards_retained=True,
        completed175_run_excluded_from_new_retrieval=True,
        runtime173_preserved=True)
    (report / 'workflow-test.json').open('x').write(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
