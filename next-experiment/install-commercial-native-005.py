"""Install only the verified commercial diagnostic overlay; retain all existing entries."""
from pathlib import Path
source=Path(__file__).with_name('install-commercial-native-002.py').read_text().replace('commercial61-native-002','commercial61-native-005').replace('minimal startup 002','profile observer 005')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
