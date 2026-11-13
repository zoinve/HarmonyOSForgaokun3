from pathlib import Path
source=Path(__file__).with_name('run-native-gpu-probe-036.py').read_text().replace('native-gpu-probe-036','native-gpu-probe-040')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
