"""Actual previous configuration: restore vendor resources without extra grants."""
from pathlib import Path
import copy,json,runpy,unittest
base=Path(__file__).resolve().parent
assert (base/'commercial-mapper-path-023.py').is_file(),'missing vendor passthrough repair'
repair=runpy.run_path(str(base/'commercial-mapper-path-023.py'))['repair']
class MapperPath(unittest.TestCase):
    def test_only_existing_vendor_source_changes(self):
        old=json.loads((base.parent/'reports/commercial61-native-022/alias-appdata-sandbox.json').read_text())
        saved=copy.deepcopy(old);new=repair(old)
        self.assertEqual(old,saved)
        block=next(g['com.ohos.sceneboard'][0] for g in new['individual'] if 'com.ohos.sceneboard' in g)
        mount=next(m for m in block['mount-paths'] if m['sandbox-path']=='/vendor/lib64/passthrough')
        self.assertEqual(mount['src-path'],'/vendor/lib64/passthrough')
        self.assertEqual(mount['check-action-status'],'true')
        mount['src-path']='/system/lib64'
        self.assertEqual(new,old)
        with self.assertRaises(AssertionError):repair(repair(old))
if __name__=='__main__':unittest.main()
