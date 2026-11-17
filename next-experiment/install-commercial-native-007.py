from pathlib import Path
source=Path(__file__).with_name('install-commercial-native-006.py').read_text().replace('commercial61-native-006','commercial61-native-007').replace('profile observer 006','profile observer 007')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
