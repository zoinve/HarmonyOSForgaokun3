"""Retain 093 hardware checks and cover the original CLI's whitespace format."""
from pathlib import Path

BASE = Path(__file__).resolve().parent
source = (BASE/'test-commercial-admission-093.py').read_text().replace("('092', '093')", "('092', '094')").replace(
    'commercial61-native-093', 'commercial61-native-094').replace('commercial-workflow-093.py', 'commercial-workflow-094.py').replace(
    "['source093']", "['source094']").replace('early093.img', 'early094.img')
anchor = "[('valid-identity', identity, 0), ('short-identity', b'123', 0), ('denied-identity', b'', 1)]"
assert source.count(anchor) == 1
source = source.replace(anchor, "[('valid-identity', identity, 0), ('original-cli-whitespace', b'    '+identity+b'\\r', 0), ('short-identity', b'123', 0), ('denied-identity', b'', 1)]", 1)
source = source.replace("if name == 'valid-identity':", "if name in ('valid-identity', 'original-cli-whitespace'):")
source = source.replace('three_original_parameter_digest_scenarios_pass', 'four_original_parameter_digest_scenarios_pass')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
