"""Reuse exact ordered-overlay verification for the smaller 105 delta."""
from pathlib import Path

BASE = Path(__file__).resolve().parent
source = (BASE/'build-commercial-overlay-104.py').read_text()
source = source.replace('commercial61-native-104', '__CANDIDATE__').replace(
    'commercial61-native-101', 'commercial61-native-104').replace('__CANDIDATE__', 'commercial61-native-105')
source = source.replace('ordered_chain_equals_full_104', 'ordered_chain_equals_full_105')
old = "'native-target/reference-stack-probe103', 'native-target/commercial-server-stack104.sh'"
assert source.count(old) == 1
source = source.replace(old, "'native-target/commercial-server-stack105.sh'", 1)
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
