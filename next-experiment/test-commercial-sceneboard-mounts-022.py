"""Two board-specific source aliases must not change sandbox permissions."""
from pathlib import Path
import copy,runpy,unittest
repair=runpy.run_path(str(Path(__file__).with_name('commercial-sceneboard-mounts-022.py')))['repair']

class Mounts(unittest.TestCase):
    def fixture(self):
        return {'common':[{'app-base':[{'mount-paths':[{'src-path':'/system/lib64','sandbox-path':'/system/lib64'}]}]}],
                'individual':[{'other.app':[{'sandbox-switch':'ON'}], 'com.ohos.sceneboard':[{
                    'sandbox-switch':'ON','gids':[1065],'symbol-links':[], 'mount-paths':[
                        {'src-path':src,'sandbox-path':dst,'sandbox-flags':['bind','rec'],'check-action-status':'true'}
                        for src,dst in [('/data/app/el1/bundle/public/','/data/app/el1/bundle/public/'),
                            ('/data/local/tmp/l410-sceneboard-r18-passthrough-v2','/vendor/lib64/passthrough'),
                            ('/data/local/tmp/l410-fp-completion-v3/SceneBoard','/system/app/SceneBoard')]]}]}],
                'permission':{'untouched':True}}
    def test_only_two_existing_resource_sources_change(self):
        old=self.fixture();saved=copy.deepcopy(old);new=repair(old)
        self.assertEqual(old,saved)
        mounts=new['individual'][0]['com.ohos.sceneboard'][0]['mount-paths']
        self.assertEqual(mounts[1]['src-path'],'/system/lib64')
        self.assertEqual(mounts[2]['src-path'],'/system/app/SceneBoard')
        mounts[1]['src-path']=saved['individual'][0]['com.ohos.sceneboard'][0]['mount-paths'][1]['src-path']
        mounts[2]['src-path']=saved['individual'][0]['com.ohos.sceneboard'][0]['mount-paths'][2]['src-path']
        self.assertEqual(new,saved)
    def test_reject_unknown_or_disabled_configuration(self):
        for mutate in [lambda b:b.update({'sandbox-switch':'OFF'}),
                       lambda b:b['mount-paths'][1].update({'check-action-status':'false'}),
                       lambda b:b['mount-paths'][1].update({'src-path':'/unknown'})]:
            old=self.fixture();mutate(old['individual'][0]['com.ohos.sceneboard'][0])
            with self.assertRaises(AssertionError):repair(old)
        with self.assertRaises(AssertionError):repair(repair(self.fixture()))

if __name__=='__main__':unittest.main()
