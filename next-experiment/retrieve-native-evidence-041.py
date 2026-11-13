from pathlib import Path
source=Path(__file__).with_name('retrieve-native-evidence-033.py').read_text().replace('native-original-graphics-boot-033','native-original-graphics-boot-041').replace('native-interactive-033','native-interactive-041').replace('harmony-return-audit-033','harmony-return-audit-041')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
