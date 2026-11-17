from pathlib import Path

source = Path(__file__).with_name('retrieve-commercial-partial-048.py').read_text()
source = source.replace('commercial61-native-048', 'commercial61-native-049').replace('commercial-return-audit-048', 'commercial-return-audit-049').replace('commercial-workflow-048.py', 'commercial-workflow-049.py')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
