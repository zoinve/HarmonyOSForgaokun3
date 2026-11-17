"""Only the audited Ubuntu diagnostic boot may supplement the standard host."""
from pathlib import Path
import runpy,unittest

class HostGuard(unittest.TestCase):
    def test_pinned_diagnostic_host_and_unchanged_default(self):
        module=Path(__file__).with_name('commercial-host-023.py')
        self.assertTrue(module.exists(),'missing audited-host guard')
        check=runpy.run_path(str(module))['validate']
        default='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
        state=dict(status='Default Entry: '+default+'\nCurrent Entry: ego-s4diag-20261113.conf\n',
            boot_id='f6df309e-a8c1-4f00-8ec6-fc6e421f0e85',release='7.1.0-rc3-gaokun3-ego-s4diag1',
            root_uuid='ecdd7931-ca18-4d14-82cd-ba3c62ff7365',os_id='ubuntu',
            entry_sha256='0c505e8371daa2615ad47e9bda4f575cdaa634e122b60b5f6d7cfe91dd52ebfd')
        check(state)
        for field in state:
            bad=dict(state);bad[field]='unexpected'
            with self.subTest(field=field),self.assertRaises(AssertionError):check(bad)
        bad=dict(state);bad['status']+='OneShot Entry: other.conf\n'
        with self.assertRaises(AssertionError):check(bad)

if __name__=='__main__':unittest.main()
