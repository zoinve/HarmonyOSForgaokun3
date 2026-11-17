"""Keep 063 account ordering; observe public boot state and ACLs only."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-063.py'))
helper = runpy.run_path(str(b / 'commercial-event-state-064.py'))
inner = p['inner']
outer = helper['instrument_outer'](p['outer'])
outer = outer.replace('commercial61-native-063', 'commercial61-native-064').replace('COMMERCIAL063', 'COMMERCIAL064')
payload = p['payload'].replace('outer=' + repr(p['outer']), 'outer=' + repr(outer), 1)
payload = payload.replace('commercial61-native-063', 'commercial61-native-064')
assert payload.count("base/'commercial-account-order-063.py'") == 1
payload = payload.replace("base/'commercial-account-order-063.py'", "base/'commercial-event-state-064.py'", 1)
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
