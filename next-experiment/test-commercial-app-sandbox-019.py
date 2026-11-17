"""Only an alias of an already exposed library tree; never alter seccomp."""
from pathlib import Path
import copy, runpy, unittest

base = Path(__file__).resolve().parent
assert (base/'commercial-app-sandbox-019.py').exists(), 'missing narrow application-library path alias'
repair = runpy.run_path(str(base/'commercial-app-sandbox-019.py'))['repair']

class AliasTests(unittest.TestCase):
    def fixture(self):
        return {'common':[{'top-sandbox-switch':'ON', 'app-base':[{
            'sandbox-root':'/mnt/sandbox/<currentUserId>/<PackageName>',
            'mount-paths':[{'src-path':'/system/lib64','sandbox-path':'/system/lib64',
                            'sandbox-flags':['bind','rec'],'check-action-status':'false'}],
            'symbol-links':[], 'flags-point':[]}]}], 'individual':{'unchanged':True}}

    def test_preserves_all_existing_rules_and_requires_new_alias(self):
        original=self.fixture(); snapshot=copy.deepcopy(original)
        new=repair(original)
        mounts=new['common'][0]['app-base'][0]['mount-paths']
        self.assertEqual(mounts[-1], {'src-path':'/system/lib64',
            'sandbox-path':'/usr/system/lib64','sandbox-flags':['bind','rec'],
            'check-action-status':'true'})
        mounts.pop()
        self.assertEqual(new,snapshot)
        self.assertEqual(original,snapshot)

    def test_rejects_ungranted_or_conflicting_alias(self):
        original=self.fixture(); original['common'][0]['app-base'][0]['mount-paths']=[]
        with self.assertRaises(AssertionError): repair(original)
        with self.assertRaises(AssertionError): repair(repair(self.fixture()))
        original=self.fixture()
        original['common'][0]['app-base'][0]['symbol-links']=[{'link-name':'/usr','target-name':'/'}]
        with self.assertRaises(AssertionError): repair(original)

if __name__=='__main__': unittest.main()
