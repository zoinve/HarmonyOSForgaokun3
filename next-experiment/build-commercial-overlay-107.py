"""Pack the 107 observation delta and verify the entire ordered archive chain."""
from pathlib import Path
import runpy

BASE = Path(__file__).resolve().parent
source = runpy.run_path(str(BASE / 'build-commercial-overlay-105.py'))['source']
source = source.replace('commercial61-native-105', '__NEW__').replace('commercial61-native-104', 'commercial61-native-105').replace('__NEW__', 'commercial61-native-107')
source = source.replace('commercial-server-stack105', 'commercial-server-stack107').replace('ordered_chain_equals_full_105', 'ordered_chain_equals_full_107')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
