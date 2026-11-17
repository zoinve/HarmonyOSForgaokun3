from pathlib import Path
import hashlib
import io
import runpy
import tarfile
import tempfile
import unittest

API = runpy.run_path(str(Path(__file__).with_name('prepare-settings-preinstall-state-189.py')))


class Tests(unittest.TestCase):
    def fixture(self, payload=b'abc', uid=10):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        path = Path(folder.name) / 'fixture.tar.gz'
        with tarfile.open(path, 'w:gz') as archive:
            entry = tarfile.TarInfo('service/el1/public/bms/fixture.db')
            entry.size, entry.uid, entry.gid, entry.mode = len(payload), uid, 20, 0o600
            archive.addfile(entry, io.BytesIO(payload))
        expected = [dict(path=entry.name, bytes=3, kind=0o100000, uid=10, gid=20,
                         mode=0o600, sha256=hashlib.sha256(b'abc').hexdigest())]
        return path, expected

    def test_reread_verifies_payload_and_owners(self):
        path, expected = self.fixture()
        API['verify_archive'](path, expected)

    def test_changed_payload_rejected(self):
        path, expected = self.fixture(payload=b'bad')
        with self.assertRaises(AssertionError):
            API['verify_archive'](path, expected)

    def test_changed_owner_rejected(self):
        path, expected = self.fixture(uid=99)
        with self.assertRaises(AssertionError):
            API['verify_archive'](path, expected)

    def test_install_state_and_parents(self):
        for path in ['app', 'app/el1', 'app/el1/bundle/public/a/libs/arm64/a.so',
                     'service/el1/public/bms/bundle_manager_service/bmsdb.db',
                     'service/el1/public/access_token/access_token.db']:
            self.assertEqual(API['relative_selected']('./.hmos-data/' + path), path)

    def test_identity_and_credentials_excluded(self):
        for path in ['service/el0/startup/init/persist_parameters', 'service/el1/public/account/state.db',
                     'service/el1/public/sshd/ssh_host_key', 'vendor/l410-linux/rootfs-bookworm/root/.ssh/id_rsa',
                     'app/el2/100/base/com.huawei.hmos.settings/preferences/a.xml']:
            self.assertIsNone(API['relative_selected']('./.hmos-data/' + path))

    def test_path_safety(self):
        for path in ['./.hmos-data/app/../service/el0/access_token/a',
                     './.hmos-data\r/service/el0/access_token/a',
                     './.hmos-data//service/el0/access_token/a',
                     './.hmos-data/service/el1/public/bms-other/a', '/etc/passwd']:
            self.assertIsNone(API['relative_selected'](path))


if __name__ == '__main__':
    unittest.main()
