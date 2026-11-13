from pathlib import Path
source=Path(__file__).with_name('run-native-gpu-composer-test-041.py').read_text().replace('native-gpu-composer-041-tests','native-gpu-formats-042-tests').replace('native-gpu-composer-test-041','native-gpu-formats-042').replace('PASS: real GPU RGB','PASS: real GPU 32')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
