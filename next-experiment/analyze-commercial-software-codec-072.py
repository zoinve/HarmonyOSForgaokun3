"""Count real original-service outcomes; helper readiness is not decode proof."""
from pathlib import Path
import hashlib
import json
import re

base = Path(__file__).resolve().parents[1] / 'reports'


def observe(number):
    root = base / ('commercial61-native-' + number)
    raw = root / 'runtime-evidence/raw'
    manifest = json.loads((raw.parent / 'retrieval-manifest.json').read_text())
    for name, item in manifest['files'].items():
        data = (raw / name).read_bytes()
        assert len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256']
    hilog = (raw / 'interactive-hilog030.log').read_text(errors='replace').splitlines()
    faults = (raw / 'interactive-faults030.log').read_bytes()
    patterns = dict(hevc_decoder_create_failed='hevc deocder create failed',
        avc_open_failed='Start codec failed: cannot open avcodec',
        video_decode_error='331350556', media_source_failed='Video media player set media source failed')
    matched = {key: [line for line in hilog if needle in line] for key, needle in patterns.items()}
    pattern = (rb'COMMERCIAL043_STREAM_BEGIN sample=(\d+) pid=(\d+) path=(\S+) limit=(\d+)\n'
        rb'(.*?)\nCOMMERCIAL043_STREAM_END sample=\1 pid=\2 path=\3 bytes=(\d+) eof=(\d+) errno=(\d+)')
    logs = []
    for match in re.finditer(pattern, faults, re.S):
        if not any(match[3].endswith(name) for name in [b'/l410-kylin-h264-decoder.log', b'/l410-kylin-video-decoder.log']):
            continue
        body = match[5]
        assert len(body) == int(match[6]) <= int(match[4])
        logs.append(dict(sample=int(match[1]), pid=int(match[2]), path=match[3].decode(),
            bytes=len(body), eof=int(match[7]), errno=int(match[8]), body=body.decode(errors='replace')))
    return dict(run=manifest['run'], verified_files=len(manifest['files']),
        counts={key: len(lines) for key, lines in matched.items()}, matched_messages=matched,
        helper_log_streams=logs,
        helper_ready_modes=sorted({mode for mode in ['ring', 'legacy'] if any(
            'SOFTWARE_CODEC_READY mode=' + mode + ' uid=1013 ' in row['body'] for row in logs)}),
        original_helper_exit_lines=[line.decode(errors='replace') for line in faults.splitlines()
            if b'l410_kylin_' in line and (b'exit' in line.lower() or b'restart' in line.lower())])


result = dict(baseline=observe('071'), candidate=observe('072'),
    helper_readiness_is_not_decode_proof=True, desktop_verified=False, interaction_verified=False)
with (base / 'commercial61-native-072/software-codec-analysis.json').open('x') as f:
    json.dump(result, f, indent=2)
print(json.dumps({key: {k: v for k, v in value.items() if k not in [
    'matched_messages', 'helper_log_streams', 'original_helper_exit_lines']}
    for key, value in result.items() if isinstance(value, dict)}, indent=2))
