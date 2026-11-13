"""Verify only an ordinary init start command is added to the boot job."""
import json
import re
import runpy
from pathlib import Path

base = Path(__file__).resolve().parent
source = (base / 'payload-919/init.c').read_text()
transform = runpy.run_path(str(base / 'hdc-start.py'))['hdc_start']
changed = transform(source)
def config(text):
    literal = re.search(r'const char mainconfig\[\] = (".*?");', text).group(1)
    return json.loads(json.loads(literal))
before, after = config(source), config(changed)
boot = next(j for j in after['jobs'] if j['name'] == 'boot')
assert boot['cmds'].pop() == 'start hdcd'
assert after == before
addition = r', \"start hdcd\"'
assert changed.replace(addition, '', 1) == source
assert transform(changed) == changed
print('PASS: original daemon started once by normal boot job; security/config unchanged')
