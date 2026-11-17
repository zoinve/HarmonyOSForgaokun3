from pathlib import Path
source=Path(__file__).with_name('run-commercial-native-001.py').read_text().replace('commercial61-native-001','commercial61-native-007')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
