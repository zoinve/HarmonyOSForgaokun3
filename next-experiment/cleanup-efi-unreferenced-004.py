"""Use the existing backup-before-removal procedure for one unreferenced payload."""
from pathlib import Path

BASE=Path(__file__).resolve().parent
if __name__=='__main__':
    source=(BASE/'cleanup-efi-unreferenced-002.py').read_text()
    assert source.count('efi-unreferenced-cleanup-002')==2
    source=source.replace('efi-unreferenced-cleanup-002','efi-unreferenced-cleanup-004')
    exec(compile(source,'cleanup-efi-unreferenced-004.generated.py','exec'),
        {'__name__':'__main__','__file__':__file__})
