"""One bounded real-helper offscreen test; does not boot or modeset HarmonyOS."""
from pathlib import Path
source=Path(__file__).with_name('run-native-gpu-probe-036.py').read_text()
source=source.replace('native-gpu-probe-036/gpu-probe','native-gpu-composer-041-tests/gpu-composer-test')
source=source.replace('native-gpu-probe-036','native-gpu-composer-test-041')
source=source.replace('PASS: hardware rotation','PASS: real GPU RGB')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
