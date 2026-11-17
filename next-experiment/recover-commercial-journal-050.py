from pathlib import Path

source = Path(__file__).with_name('recover-commercial-journal-048.py').read_text()
source = source.replace('commercial61-native-048', 'commercial61-native-050').replace('commercial-recovery-048', 'commercial-recovery-050').replace('commercial-workflow-048.py', 'commercial-workflow-050.py')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
