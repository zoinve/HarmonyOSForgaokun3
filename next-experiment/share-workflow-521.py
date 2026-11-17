"""Install/boot517 once, reusing the already installed kernel490 unchanged."""
from pathlib import Path

BASE=Path(__file__).resolve().parent

if __name__ == '__main__':
    source=(BASE/'share-kernel-workflow-505.py').read_text()
    source=source.replace('commercial61-native-502','commercial61-native-517')
    source=source.replace('commercial61-native-471','commercial61-native-502')
    source=source.replace('set502.img','set517.img').replace('set471.img','set502.img')
    source=source.replace('retired-entry-471','retired-entry-502').replace('prior471_','prior502_')
    source=source.replace('kernel 502 -','kernel 517 -')
    source=source.replace(' and not kernel.exists()', ' and kernel.is_dir()')
    source=source.replace("old.count('linux /native-original-graphics-045/linux')", "old.count('linux /native-compat-kernel-490/linux')")
    source=source.replace("+len(decoded['kernel490'])", '')
    old="kernel.mkdir()\nwrite(kernel/'linux',decoded['kernel490'],0o600)"
    assert source.count(old)==1
    source=source.replace(old,"assert (kernel/'linux').read_bytes()==decoded['kernel490']")
    exec(compile(source,str(BASE/'share-workflow-521.generated.py'),'exec'),
         dict(__name__='__main__',__file__=str(BASE/'share-workflow-521.generated.py')))
