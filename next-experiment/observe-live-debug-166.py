"""Observe the persistent-data boot with the already verified read-only channel."""
from pathlib import Path

BASE=Path(__file__).resolve().parent
if __name__=='__main__':
    source=(BASE/'observe-live-debug-161.py').read_text()
    source=source.replace('commercial61-native-161','commercial61-native-166-compile-fix-1')
    source=source.replace('harmony-native-161','harmony-native-166')
    exec(compile(source,'observe-live-debug-166.wrapper.py','exec'),
        {'__name__':'__main__','__file__':str(BASE/'observe-live-debug-166.wrapper.py')})
