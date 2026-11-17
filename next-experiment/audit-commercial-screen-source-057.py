"""Archive pinned upstream sources as supporting evidence, not binary identity."""
from pathlib import Path
import hashlib
import json
import urllib.request

BASE = Path(__file__).resolve().parents[1]
COMMIT = '0fa4396a14a9717472a45ca45f184338760f720a'
PATHS = [
    'rosen/modules/render_service/core/drawable/rs_screen_render_node_drawable.cpp',
    'rosen/modules/render_service_base/include/params/rs_screen_render_params.h',
    'rosen/modules/render_service_base/src/params/rs_screen_render_params.cpp',
    'rosen/modules/render_service_base/src/pipeline/rs_screen_render_node.cpp',
]


def main():
    out = BASE / 'reports/commercial-screen-source-audit-057'
    assert not out.exists(), 'Preserve numbered source evidence'
    downloaded = []
    for path in PATHS:
        url = 'https://raw.githubusercontent.com/openharmony/graphic_graphic_2d/' + COMMIT + '/' + path
        with urllib.request.urlopen(url, timeout=30) as response:
            assert response.status == 200
            body = response.read()
        downloaded.append((path, url, body))
    texts = {Path(path).name: body.decode() for path, _, body in downloaded}
    drawable = texts['rs_screen_render_node_drawable.cpp']
    start = drawable.index('void RSScreenRenderNodeDrawable::OnDraw(Drawing::Canvas& canvas)')
    initial = drawable[start:start+2200]
    for value in ['GetChildDisplayCount() == 0', 'DrawSkipType::NO_DISPLAY_NODE',
                  'DrawSkipType::RENDER_PARAMS_OR_UNI_PARAMS_NULL', 'DrawSkipType::SCREEN_STATE_INVALID',
                  'CheckRenderSkipIfScreenOff(true, params->GetScreenId())']:
        assert value in initial, value
    assert 'screenParams->childDisplayCount_ = GetChildrenCount();' in texts['rs_screen_render_node.cpp']
    assert 'targetScreenParams->childDisplayCount_ =  childDisplayCount_;' in texts['rs_screen_render_params.cpp']
    out.mkdir()
    files = []
    for path, url, body in downloaded:
        name = Path(path).name
        (out / name).open('xb').write(body)
        files.append(dict(path=name, upstream_path=path, url=url, bytes=len(body), sha256=hashlib.sha256(body).hexdigest()))
    result = dict(repository='openharmony/graphic_graphic_2d', commit=COMMIT,
                  branch_at_resolution='OpenHarmony-6.0-Release', files=files,
                  supporting_source_only=True, commercial_binary_identity_claimed=False,
                  kernel_or_userland_changed=False, desktop_verified=False,
                  runtime057_initial_gate_samples=0,
                  interpretation='Upstream no-display-node branch was not observed in 057; do not claim it caused the black screen')
    (out / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(dict(commit=COMMIT, files=len(files), supporting_source_only=True,
                          commercial_binary_identity_claimed=False), indent=2))


if __name__ == '__main__':
    main()
