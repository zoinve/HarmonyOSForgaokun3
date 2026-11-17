"""Correlate the unchanged 132-second physical-keyboard observation in 099."""
from pathlib import Path
import runpy

BASE = Path(__file__).resolve().parent
source = runpy.run_path(str(BASE/'analyze-commercial-input-response-078.py'))['source']
source = source.replace("else '078'", "else '099'").replace(
    "['075', '076', '077', '078']", "['075', '076', '077', '078', '099']")
anchor = "re.match(r'01-01 08:02:1[23]\\.',line)"
assert source.count(anchor) == 1
source = source.replace(anchor,
    "any(public_stamp099(line) is not None and public_stamp099(event['text']) is not None "
    "and 0 <= public_stamp099(line)-public_stamp099(event['text']) <= 0.5 for event in events)", 1)
helpers = '''
import datetime
def public_stamp099(line):
    match = re.match(r'^(\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}\\.\\d{3})', line)
    if not match:
        return None
    return datetime.datetime.strptime('2000-'+match[1], '%Y-%m-%d %H:%M:%S.%f').timestamp()
'''
source = source.replace('number = sys.argv[1]', helpers+'\nnumber = sys.argv[1]', 1)
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
