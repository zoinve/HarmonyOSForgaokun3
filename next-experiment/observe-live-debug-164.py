"""One distinct native-164 observation with unchanged authenticated discovery protocol."""
from pathlib import Path

BASE=Path(__file__).resolve().parent


if __name__=='__main__':
    source=(BASE/'observe-live-debug-161.py').read_text()
    source=source.replace('commercial61-native-161','commercial61-native-164').replace('harmony-native-161','harmony-native-164')
    source=source.replace('observe-live-debug-161.generated.py','observe-live-debug-164.generated.py')
    exec(compile(source,'observe-live-debug-164.wrapper.py','exec'),{'__name__':'__main__','__file__':str(BASE/'observe-live-debug-164.wrapper.py')})
