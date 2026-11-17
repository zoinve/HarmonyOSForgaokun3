from pathlib import Path

source = Path(__file__).with_name('analyze-commercial-boundaries-048.py').read_text()
source = source.replace('commercial61-native-048', 'commercial61-native-049').replace('COMMERCIAL048', 'COMMERCIAL049')
anchor = '    result = dict(run=manifest[\'run\'],'
assert source.count(anchor) == 1
source = source.replace(anchor, '    stages = re.findall(r"COMMERCIAL049_TRACE_STAGE [^\\n]+", text)\n    result = dict(stages=stages, last_stage=stages[-1] if stages else None, run=manifest[\'run\'],', 1)
source = source.replace("if k != 'controls'", "if k not in ['controls', 'stages']")
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
