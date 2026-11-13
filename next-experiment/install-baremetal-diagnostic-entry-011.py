"""Independent014 entry; preserve Ubuntu defaults and64MiB ESP reserve."""
from pathlib import Path
import ast
import runpy
def launcher_source():
    source=runpy.run_path(str(Path(__file__).with_name('install-baremetal-diagnostic-entry-010.py')))['launcher_source']()
    for old,new in [('baremetal-boot-entry-preflight-010.json','baremetal-boot-entry-preflight-011.json'),
                    ('baremetal-boot-entry-installed-010.json','baremetal-boot-entry-installed-011.json'),
                    ('boot-entry-install-010','boot-entry-install-011'),
                    ('harmony-native-diag-013','harmony-native-diag-014'),
                    ('native-identity-diagnostic-013','native-identity-diagnostic-014'),
                    ('17b8eb520e7185c568520cc2e4c1e5d1eb168058a98cbbb23e28e78dcf79e3d7','801eaaf844aea65d3d57df7350b488ebbd8793c3187fd6666e283e5c7960455b'),
                    ('identity and allocator diagnostic 013','identity and cross-process GPU diagnostic 014')]:
        assert old in source,old
        source=source.replace(old,new)
    ast.parse(source)
    return source
if __name__=='__main__':exec(compile(launcher_source(),__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})
