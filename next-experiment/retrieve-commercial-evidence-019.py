from pathlib import Path
source=Path(__file__).with_name('retrieve-commercial-evidence-018.py').read_text().replace('commercial61-native-018','commercial61-native-019').replace('commercial-return-audit-018','commercial-return-audit-019')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
