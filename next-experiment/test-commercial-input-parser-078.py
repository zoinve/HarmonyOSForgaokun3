from pathlib import Path
import re
import runpy

module = runpy.run_path(str(Path(__file__).with_name('analyze-commercial-input-response-078.py')))
for stamp in ['132968086', ' 132968086 ', '  132968086']:
    line = '[K:D:1][HandleKeyboardEvent:477] KC:2076,AT:' + stamp + ', ET:key, KA:KEY_ACTION_DOWN'
    assert re.search(module['INPUT_PATTERN'], line).groups() == ('D', '1', '132968086', 'DOWN')
assert re.search(module['INPUT_PATTERN'], '[K:U:2] AT:133048180, KA:KEY_ACTION_UP').groups() == ('U','2','133048180','UP')
assert re.search(module['INPUT_PATTERN'], '[K:D:1] AT:unknown, KA:KEY_ACTION_DOWN') is None
assert "r'COMMERCIAL075_KEYBOARD" in module['source']
compile(module['source'], '078-input-analysis', 'exec')
print('PASS: compact/spaced timestamps, down/up, malformed rejection, unchanged writer marker')
