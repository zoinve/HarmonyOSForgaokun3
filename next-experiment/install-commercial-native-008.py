from pathlib import Path
source=Path(__file__).with_name('install-commercial-native-002.py').read_text().replace('commercial61-native-002','commercial61-native-008').replace('minimal startup 002','sandbox path alias 008')
source=source.replace("if __name__=='__main__':exec(","source=source.replace('AUTO RETURN 7 MIN','AUTO RETURN 210 SEC')\nif __name__=='__main__':exec(")
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
