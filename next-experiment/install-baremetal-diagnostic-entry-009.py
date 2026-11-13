"""Install independent allocator013 assets; never select or reboot here."""
from pathlib import Path
import ast
import runpy
def launcher_source():
    source=runpy.run_path(str(Path(__file__).with_name('install-baremetal-diagnostic-entry-008.py')))['launcher_source']()
    for old,new in [('baremetal-boot-entry-preflight-008.json','baremetal-boot-entry-preflight-009.json'),
                    ('baremetal-boot-entry-installed-008.json','baremetal-boot-entry-installed-009.json'),
                    ('boot-entry-install-008','boot-entry-install-009'),
                    ('harmony-native-diag-011','harmony-native-diag-013'),
                    ('native-identity-diagnostic-011','native-identity-diagnostic-013'),
                    ('9737f1ad608b34e91750be64fc7360be4ac407ab1fd0ffb4a44eb721973efb84','17b8eb520e7185c568520cc2e4c1e5d1eb168058a98cbbb23e28e78dcf79e3d7'),
                    ('native identity and offscreen GPU diagnostic 011','native identity and allocator diagnostic 013')]:
        assert old in source,old
        source=source.replace(old,new)
    assert source.count('enforcing=1')==1
    ast.parse(source)
    return source
if __name__=='__main__':exec(compile(launcher_source(),__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})
