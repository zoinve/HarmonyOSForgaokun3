"""Counted trial; retain native015 kernel/DTB and original initrd archive."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-native-original-graphics-boot-010.py')))['source']
source=source.replace('boot-010','boot-011').replace('graphics-010','graphics-011').replace('trial 010','trial 011')
source=source.replace('diagnostic-014','diagnostic-015').replace('diag-014','diag-015').replace('801eaaf844aea65d3d57df7350b488ebbd8793c3187fd6666e283e5c7960455b','2521acd99c47bf5465ea5ed2fe0eb0d687491350d4956058f8de5d4309abae53')
# Native015's kernel/DTB are referenced, but its obsolete initrd is not.
# Check the exact BLS argument rather than rejecting every file in that folder.
needle="assert not any('/'+str(p.parent.relative_to(esp))+'/' in text for text in loader.values())"
assert source.count(needle)==1
source=source.replace(needle,"assert not any('/'+str(p.relative_to(esp)) in text.split() for text in loader.values())")
if __name__=='__main__':
 exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
