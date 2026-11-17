"""Independent diagnostic overlay; no change to commercial service payload."""
from pathlib import Path
source=Path(__file__).with_name('install-commercial-native-002.py').read_text()
source=source.replace('commercial61-native-002','commercial61-native-003').replace('minimal startup 002','diagnostic capture 003')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
