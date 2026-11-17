"""Compare authenticated original-service messages, never equate readiness with decode."""
from pathlib import Path
import hashlib
import json

b = Path(__file__).resolve().parents[1] / 'reports'
patterns = dict(codec_allocation_failed='Start codec failed: cannot allocate buffers',
    surface_allocation_failed='Alloc surface buffer failed',
    allocator_minus_two='AllocMem: AllocMem failed, ec = -2',
    proxy_minus_two='AllocMem_ failed, error code is -2',
    avc_open_failed='Start codec failed: cannot open avcodec',
    hevc_create_failed='hevc deocder create failed',
    video_error='331350556', media_source_failed='Video media player set media source failed')


def observe(number):
    raw = b / ('commercial61-native-' + number) / 'runtime-evidence/raw'
    manifest = json.loads((raw.parent / 'retrieval-manifest.json').read_text())
    for name, item in manifest['files'].items():
        body = (raw / name).read_bytes()
        assert len(body) == item['bytes'] and hashlib.sha256(body).hexdigest() == item['sha256']
    lines = (raw / 'interactive-hilog030.log').read_text(errors='replace').splitlines()
    matched = {key: [line for line in lines if text in line] for key, text in patterns.items()}
    return dict(run=manifest['run'], counts={key: len(rows) for key, rows in matched.items()},
        matched_messages=matched,
        codec_messages=[line for line in lines if '/FCodec:' in line or '/HevcDecoderLoader:' in line],
        egl_import_messages=[line for line in lines if 'eglCreateImage' in line or 'CreateEglImage' in line])


result = dict(baseline=observe('073'), candidate=observe('074'),
    line_counts_are_not_independent_failure_counts=True,
    helper_readiness_is_not_decode_proof=True, native_decoded_frames_verified=False,
    gpu_import_verified=False, desktop_verified=False, interaction_verified=False)
(b / 'commercial61-native-074/video-outcome-analysis.json').open('x').write(json.dumps(result, indent=2))
print(json.dumps({key: dict(run=result[key]['run'], counts=result[key]['counts'])
                  for key in ['baseline', 'candidate']}, indent=2))
