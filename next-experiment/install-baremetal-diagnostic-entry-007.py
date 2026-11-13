"""Independent010 entry; preserve Ubuntu and all post-cleanup EFI files."""
from pathlib import Path
import ast
import runpy

def launcher_source():
    source=runpy.run_path(str(Path(__file__).with_name('install-baremetal-diagnostic-entry-006.py')))['launcher_source']()
    for old,new in [
        ('baremetal-boot-entry-preflight-006.json','baremetal-boot-entry-preflight-007.json'),
        ('baremetal-boot-entry-installed-006.json','baremetal-boot-entry-installed-007.json'),
        ('boot-entry-install-006','boot-entry-install-007'),
        ('harmony-native-diag-009','harmony-native-diag-010'),
        ('native-identity-diagnostic-009','native-identity-diagnostic-010'),
        ('c249d700d67c14dbd3c97182a823c14ecd9dde3102a9ff9aae358576f20b1d4c','f00ae673e495abbd521628418badbc16d7f12d72d40236855b0a7f149e0e5afb'),
        ('native identity and hardware diagnostic 009','native identity and offscreen GPU diagnostic 010'),
    ]:
        assert old in source,old;source=source.replace(old,new)
    assert source.count('enforcing=1')==1
    ast.parse(source);return source

if __name__=='__main__':exec(compile(launcher_source(),__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})
