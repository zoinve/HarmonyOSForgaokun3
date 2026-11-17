'''Observe only the new Settings launch experiment through the existing read-only channel.'''
from pathlib import Path

BASE=Path(__file__).resolve().parent

if __name__=='__main__':
    source=(BASE/'observe-live-debug-197.py').read_text()
    source=source.replace('commercial61-native-197-r1','commercial61-native-201')
    source=source.replace('harmony-native-197','harmony-native-201')
    exec(compile(source,'observe-live-debug-201.generated.py','exec'),
         {'__name__':'__main__','__file__':str(BASE/'observe-live-debug-201.generated.py')})
