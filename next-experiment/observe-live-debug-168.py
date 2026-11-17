from pathlib import Path

BASE=Path(__file__).resolve().parent
if __name__=='__main__':
    source=(BASE/'observe-live-debug-166.py').read_text()
    source=source.replace('commercial61-native-166-compile-fix-1','commercial61-native-168').replace('harmony-native-166','harmony-native-168')
    exec(compile(source,'observe-live-debug-168.wrapper.py','exec'),
        {'__name__':'__main__','__file__':str(BASE/'observe-live-debug-168.wrapper.py')})
