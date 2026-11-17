from pathlib import Path

BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    source = (BASE / 'observe-live-debug-168.py').read_text()
    source = source.replace('commercial61-native-168','commercial61-native-173').replace('harmony-native-168','harmony-native-173')
    exec(compile(source,'observe-live-debug-173.generated.py','exec'),
        {'__name__':'__main__','__file__':str(BASE / 'observe-live-debug-173.generated.py')})
