"""Independent read-only post-return check, never boots a candidate."""
from pathlib import Path
base=Path(__file__).resolve().parent
source=(base/'verify-commercial-return-010.py').read_text().replace('commercial61-native-010','commercial61-native-017')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
