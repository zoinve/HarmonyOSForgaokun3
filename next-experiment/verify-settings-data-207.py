"""Verify206's real storage lifecycle and read-only offline state, preserving202."""
from pathlib import Path

BASE=Path(__file__).resolve().parent
if __name__=='__main__':
    source=(BASE/'verify-settings-data-202.py').read_text()
    source=source.replace('reports/commercial61-native-201','reports/commercial61-native-206')
    source=source.replace('76d33584-471a-4e78-bab5-e417a6d5c30b','e804d33f-cc8b-4a59-bc80-9bd0bc368256')
    source=source.replace('202','207')
    exec(compile(source,str(__file__),'exec'),{'__name__':'__main__','__file__':str(__file__)})
