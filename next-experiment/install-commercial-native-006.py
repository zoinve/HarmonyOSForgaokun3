from pathlib import Path
source=Path(__file__).with_name('install-commercial-native-005.py').read_text().replace('commercial61-native-005','commercial61-native-006').replace('profile observer 005','profile observer 006')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
