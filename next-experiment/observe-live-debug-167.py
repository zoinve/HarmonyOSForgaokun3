"""Separate second-boot evidence with unchanged pinned native authentication."""
from pathlib import Path

BASE=Path(__file__).resolve().parent
if __name__=='__main__':
    source=(BASE/'observe-live-debug-166.py').read_text()
    source=source.replace('commercial61-native-166-compile-fix-1','commercial61-native-167')
    source=source.replace('harmony-native-166','harmony-native-167')
    exec(compile(source,'observe-live-debug-167.wrapper.py','exec'),
        {'__name__':'__main__','__file__':str(BASE/'observe-live-debug-167.wrapper.py')})
