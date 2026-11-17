"""Correctly inspect the vendor filesystem root, whose mountpoint is /vendor."""
from pathlib import Path

BASE=Path(__file__).resolve().parent
if __name__=='__main__':
    source=(BASE/'audit-board-driver-contracts-126.py').read_text()
    source=source.replace('reports/board-driver-contracts-126','reports/vendor-driver-contracts-128')
    old="[('p111-system.kr990-ext4-v1.img','/system'),('p109-vendor.kr990-ext4-v1.img','/vendor')]"
    assert source.count(old)==1
    source=source.replace(old,"[('p109-vendor.kr990-ext4-v1.img','')]")
    source=source.replace("path=directory+'/'+name","path=directory+'/'+name\n                target_path='/vendor'+path")
    source=source.replace("prefix.strip('/')+'-'+name","'vendor-'+name")
    source=source.replace('dict(path=path,','dict(path=target_path,')
    exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
