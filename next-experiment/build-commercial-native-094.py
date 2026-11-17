"""Unbooted 093 successor: normalize original param CLI whitespace privately."""
from pathlib import Path

BASE = Path(__file__).resolve().parent
source = (BASE/'build-commercial-native-093.py').read_text().replace('commercial61-native-093', 'commercial61-native-094')
anchor = 'identity093=$(/system/bin/param get const.product.devUdid 2>/dev/null)'
assert source.count(anchor) == 1
source = source.replace(anchor, "identity093=$(/system/bin/param get const.product.devUdid 2>/dev/null | /system/bin/tr -d ' \\r\\n')", 1)
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
