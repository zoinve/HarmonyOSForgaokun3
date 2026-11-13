"""Install independent009 native profile003 entry with explicit initial enforcing=1."""
from pathlib import Path
import ast
import runpy

def launcher_source():
    source=runpy.run_path(str(Path(__file__).with_name('install-baremetal-diagnostic-entry-005.py')))['launcher_source']()
    changes={
        'baremetal-boot-entry-preflight-005.json':'baremetal-boot-entry-preflight-006.json',
        'baremetal-boot-entry-installed-005.json':'baremetal-boot-entry-installed-006.json',
        'boot-entry-install-005':'boot-entry-install-006',
        'harmony-native-diag-008':'harmony-native-diag-009',
        'native-identity-diagnostic-008':'native-identity-diagnostic-009',
        '8ba8c0049c3608e3a72769897e718051c78addb4d73a29699714f2e49f576457':'4e7796bda71bdc95364276bbff34eb2c72593a2a9a3baa7fe2b9e5ae86e65166',
        '58159556c88dc79ca32adf15aa386dd320e18403d33b32de9c7480705761d2fe':'c249d700d67c14dbd3c97182a823c14ecd9dde3102a9ff9aae358576f20b1d4c',
        'native identity and hardware diagnostic 008':'native identity and hardware diagnostic 009',
        'rdinit=/init harmony.diag=1 clk_ignore_unused':'rdinit=/init harmony.diag=1 enforcing=1 clk_ignore_unused',
    }
    for old,new in changes.items():
        assert old in source,old
        source=source.replace(old,new)
    assert source.count('enforcing=1')==1
    ast.parse(source);return source

if __name__=='__main__':exec(compile(launcher_source(),__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})
