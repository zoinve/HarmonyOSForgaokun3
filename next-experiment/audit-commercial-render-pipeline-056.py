"""Audit original screen drawable, frame request and layer submission boundaries."""
from pathlib import Path
import subprocess

b = Path(__file__).resolve().parent
source = (b / 'audit-commercial-trace-046.py').read_text()
source = source.replace('reports/commercial-trace-audit-046', 'reports/commercial-render-audit-056').replace('commercial046/', 'commercial056/')
start = source.index('METHODS = [')
end = source.index('\n]\n', start) + 3
methods = [
    ('service', 'screen_draw', 'DrawableV2::RSScreenRenderNodeDrawable::OnDraw(', '', False),
    ('service', 'screen_request_frame', 'DrawableV2::RSScreenRenderNodeDrawable::RequestFrame(', '', False),
    ('service', 'commit_layers', 'RSUniRenderComposerAdapter::CommitLayers(', '', False),
    ('service', 'worker_root_nonnull', 'RSUniRenderThread::Render(', '', False),
]
source = source[:start] + 'METHODS = ' + repr(methods) + source[end:]
source = source.replace('va = int(found[0][0], 16)',
                        "va = int(found[0][0], 16) + (0x18 if event == 'worker_root_nonnull' else 0)")


def verify_root_branch():
    path = b.parent / 'reports/commercial-oneway-audit-045/service.so'
    text = subprocess.check_output(['llvm-objdump-19', '-d', '--no-show-raw-insn',
                                    '--start-address=0x1701b0', '--stop-address=0x1701cc', str(path)], text=True)
    for needle in ['1701b8:', 'ldr\tx8, [x0, #0x70]', '1701c4:', 'cbz\tx8, 0x170544', '1701c8:', 'pacibsp']:
        assert needle in text, needle


if __name__ == '__main__':
    verify_root_branch()
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
