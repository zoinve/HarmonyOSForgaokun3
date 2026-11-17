from pathlib import Path

source = Path(__file__).with_name('build-commercial-overlay-047.py').read_text()
source = source.replace('commercial61-native-047', 'commercial61-native-049').replace('ordered_chain_equals_full_047', 'ordered_chain_equals_full_049')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
