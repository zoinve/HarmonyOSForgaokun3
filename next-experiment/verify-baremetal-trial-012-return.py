"""Independent012 preservation, Ubuntu return and logical screen-off checks."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('verify-baremetal-trial-011-return.py')),run_name='offline_generator')['source']
for old,new in [('baremetal-native-trial-011','baremetal-native-trial-012'),
 ('boot-entry-install-011','boot-entry-install-012'),('harmony-native-diag-014','harmony-native-diag-015')]:
 assert old in source,old
 source=source.replace(old,new)
compile(source,'verify012','exec')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})
