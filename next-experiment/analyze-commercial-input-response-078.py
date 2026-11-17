"""Handle the unchanged bootstrap marker and public log whitespace variations."""
from pathlib import Path
import re

b = Path(__file__).resolve().parent
INPUT_PATTERN = r'\[K:([DU]):(\d+)\].*AT:\s*(\d+)\s*,.*KA:KEY_ACTION_(DOWN|UP)'
source = (b / 'analyze-commercial-input-response-076.py').read_text().replace(
    "else '076'", "else '078'").replace("['075', '076']", "['075', '076', '077', '078']")
anchor = "r'COMMERCIAL' + number + r'_KEYBOARD"
assert source.count(anchor) == 1
source = source.replace(anchor, "r'COMMERCIAL075_KEYBOARD", 1)
old = r'\[K:([DU]):(\d+)\].*AT:(\d+),.*KA:KEY_ACTION_(DOWN|UP)'
assert source.count(old) == 1
source = source.replace(old, INPUT_PATTERN, 1)
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
