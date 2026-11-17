"""Fresh read-only preservation checks after the unique 018 attempt."""
from pathlib import Path
source=Path(__file__).with_name('verify-commercial-return-010.py').read_text()
source=source.replace('commercial61-native-010','commercial61-native-018')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
