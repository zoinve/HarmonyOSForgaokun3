"""Counted trial with retained original historical archive."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-native-original-graphics-boot-007.py')))['source']
source=source.replace('boot-007','boot-008').replace('graphics-007','graphics-008').replace('trial 007','trial 008')
source=source.replace('diagnostic-011','diagnostic-013').replace('diag-011','diag-013').replace('9737f1ad608b34e91750be64fc7360be4ac407ab1fd0ffb4a44eb721973efb84','17b8eb520e7185c568520cc2e4c1e5d1eb168058a98cbbb23e28e78dcf79e3d7')
if __name__=='__main__':
    exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
