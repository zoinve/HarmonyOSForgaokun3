from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('run-native-original-graphics-boot-017.py')))['source']
source=source.replace('native-original-graphics-boot-017','native-original-graphics-boot-018').replace('native-original-graphics-017','native-original-graphics-018').replace('native-original-017-','native-original-018-')
mount_guard=source[source.index("import os\nlab=Path('/mnt/harmony-lab')"):source.index("mount=cmd(['findmnt'",source.index('COLLECT='))]
anchor="source,options=cmd(['findmnt','-n','-o','SOURCE,OPTIONS','--target','/mnt/harmony-lab']).split()"
assert source.count(anchor)==1
source=source.replace(anchor,mount_guard+anchor)
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
