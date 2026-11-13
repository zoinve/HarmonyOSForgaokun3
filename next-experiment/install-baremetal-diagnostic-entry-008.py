"""Install independent 011 assets without selecting them or changing Ubuntu default."""
from pathlib import Path
import ast
import runpy

def launcher_source():
    source=runpy.run_path(str(Path(__file__).with_name('install-baremetal-diagnostic-entry-007.py')))['launcher_source']()
    for old,new in [
        ('baremetal-boot-entry-preflight-007.json','baremetal-boot-entry-preflight-008.json'),
        ('baremetal-boot-entry-installed-007.json','baremetal-boot-entry-installed-008.json'),
        ('boot-entry-install-007','boot-entry-install-008'),
        ('harmony-native-diag-010','harmony-native-diag-011'),
        ('native-identity-diagnostic-010','native-identity-diagnostic-011'),
        ('f00ae673e495abbd521628418badbc16d7f12d72d40236855b0a7f149e0e5afb','9737f1ad608b34e91750be64fc7360be4ac407ab1fd0ffb4a44eb721973efb84'),
        ('native identity and offscreen GPU diagnostic 010','native identity and offscreen GPU diagnostic 011'),
    ]:
        assert old in source,old
        source=source.replace(old,new)
    assert source.count('enforcing=1')==1
    ast.parse(source)
    return source

if __name__=='__main__':exec(compile(launcher_source(),__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})
