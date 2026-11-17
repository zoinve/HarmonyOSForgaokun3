"""Recheck original image hashes and preservation after the single 004 attempt."""
from pathlib import Path
source=Path(__file__).with_name('verify-commercial-return-001.py').read_text()
source=source.replace('commercial61-native-001','commercial61-native-004')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
