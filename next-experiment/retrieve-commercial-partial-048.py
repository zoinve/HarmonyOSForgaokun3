from pathlib import Path

source = Path(__file__).with_name('retrieve-commercial-partial-047.py').read_text()
source = source.replace('commercial61-native-047', 'commercial61-native-048').replace('commercial-return-audit-047', 'commercial-return-audit-048').replace('commercial-workflow-047.py', 'commercial-workflow-048.py')
anchor = "m=Path('/mnt/commercial-return-audit-048')"
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + '\nm.mkdir(exist_ok=True)', 1)
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
