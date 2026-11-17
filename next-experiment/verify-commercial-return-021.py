from pathlib import Path
source=Path(__file__).with_name('verify-commercial-return-020.py').read_text().replace('commercial61-native-020','commercial61-native-021')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
