"""Fresh installation record for013; preserve failed009 attempt unchanged."""
from pathlib import Path
import ast
import runpy
def launcher_source():
    source=runpy.run_path(str(Path(__file__).with_name('install-baremetal-diagnostic-entry-009.py')))['launcher_source']()
    for old,new in [('baremetal-boot-entry-preflight-009.json','baremetal-boot-entry-preflight-010.json'),
                    ('baremetal-boot-entry-installed-009.json','baremetal-boot-entry-installed-010.json'),
                    ('boot-entry-install-009','boot-entry-install-010')]:
        assert old in source,old
        source=source.replace(old,new)
    ast.parse(source)
    return source
if __name__=='__main__':exec(compile(launcher_source(),__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})
