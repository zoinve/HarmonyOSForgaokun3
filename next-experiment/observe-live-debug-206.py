"""Observe206 through the existing authenticated, read-only diagnostic channel."""
from pathlib import Path

BASE=Path(__file__).resolve().parent
if __name__=='__main__':
    source=(BASE/'observe-live-debug-201.py').read_text().replace('commercial61-native-201',
        'commercial61-native-206').replace('harmony-native-201','harmony-native-206')
    exec(compile(source,str(__file__),'exec'),{'__name__':'__main__','__file__':str(__file__)})
