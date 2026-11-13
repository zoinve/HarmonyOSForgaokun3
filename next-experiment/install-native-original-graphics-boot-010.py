"""Counted trial; reclaim only an unreferenced duplicate historical initrd."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-native-original-graphics-boot-008.py')))['source']
source=source.replace('boot-008','boot-010').replace('graphics-008','graphics-010').replace('trial 008','trial 010')
source=source.replace('diagnostic-013','diagnostic-014').replace('diag-013','diag-014').replace('17b8eb520e7185c568520cc2e4c1e5d1eb168058a98cbbb23e28e78dcf79e3d7','801eaaf844aea65d3d57df7350b488ebbd8793c3187fd6666e283e5c7960455b')
if __name__=='__main__':
    exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
