"""Read original lifecycle evidence without changing seed marker names."""
from pathlib import Path

BASE=Path(__file__).resolve().parent
if __name__=='__main__':
    source=(BASE/'analyze-oobe-seed-123.py').read_text().replace('commercial61-native-123','commercial61-native-124')
    exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
