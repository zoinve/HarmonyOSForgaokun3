from pathlib import Path
source=Path(__file__).with_name('retrieve-commercial-evidence-020.py').read_text().replace('commercial61-native-020','commercial61-native-021').replace('commercial-return-audit-020','commercial-return-audit-021')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
