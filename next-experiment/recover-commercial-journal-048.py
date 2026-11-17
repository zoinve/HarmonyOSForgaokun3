from pathlib import Path
source = Path(__file__).with_name('recover-commercial-journal-047.py').read_text()
source = source.replace('commercial61-native-047', 'commercial61-native-048').replace('commercial-recovery-047', 'commercial-recovery-048').replace('commercial-workflow-047.py', 'commercial-workflow-048.py')
old = "run='commercial61-native-048-52a7e50d-5fa5-482f-a771-df64fc0b4aa8'"
assert source.count(old) == 1
replacement = '''roots=subprocess.check_output(['debugfs','-R','ls -p /',str(image)],stderr=subprocess.DEVNULL,text=True)
runs=re.findall(r'/(commercial61-native-048-[0-9a-f-]{36})/',roots)
assert len(runs)==1,roots
run=runs[0]'''
source = source.replace(old, replacement, 1)
old = "names=['phase-%03d.log'%i for i in range(1,41)]+['interactive-hilog030.log','interactive-faults030.log']"
assert source.count(old) == 1
replacement = '''listing=subprocess.check_output(['debugfs','-R','ls -p /'+run,str(image)],stderr=subprocess.DEVNULL,text=True)
names=sorted(line.split('/')[5] for line in listing.splitlines() if len(line.split('/'))>=7 and line.split('/')[5] not in ['.','..'])
assert names and all(re.fullmatch(r'[A-Za-z0-9_.-]+',name) for name in names),listing'''
source = source.replace(old, replacement, 1)
old = "previous = json.loads((DEST.parent / 'runtime-evidence/retrieval-manifest.json').read_text())"
assert source.count(old) == 1
source = source.replace(old, "previous_path = DEST.parent / 'runtime-evidence/retrieval-manifest.json'\n    previous = json.loads(previous_path.read_text()) if previous_path.exists() else {'files': {}}", 1)
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
