"""Counted trial; retain original archive of the obsolete EFI cache."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-native-original-graphics-boot-005.py')))['source']
source=source.replace('boot-005','boot-007').replace('graphics-005','graphics-007').replace('trial 005','trial 007')
source=source.replace('diagnostic-008','diagnostic-011').replace('diag-008','diag-011').replace('58159556c88dc79ca32adf15aa386dd320e18403d33b32de9c7480705761d2fe','9737f1ad608b34e91750be64fc7360be4ac407ab1fd0ffb4a44eb721973efb84')
if __name__=='__main__':
    exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
