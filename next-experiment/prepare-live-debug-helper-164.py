"""Stage only the distinct same-inode helper; preserve earlier staged artifacts."""
from pathlib import Path

BASE=Path(__file__).resolve().parent


if __name__=='__main__':
    source=(BASE/'prepare-live-debug-helper-161.py').read_text()
    for old,new in [('commercial61-native-161','commercial61-native-164'),('live-debug-helper-161','live-debug-helper-164'),
        ('live-debug161','live-debug164'),("['live161']","['live164']")]:
        source=source.replace(old,new)
    exec(compile(source,'prepare-live-debug-helper-164.generated.py','exec'),{'__name__':'__main__','__file__':str(BASE/'prepare-live-debug-helper-164.generated.py')})
