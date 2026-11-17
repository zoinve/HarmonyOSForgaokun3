"""Independent additive board-import candidate; preserve existing entries and images."""
from pathlib import Path
source=Path(__file__).with_name('install-commercial-native-002.py').read_text()
source=source.replace('commercial61-native-002','commercial61-native-004').replace('minimal startup 002','original HDF board import 004')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
