from pathlib import Path
import subprocess

b = Path(__file__).resolve().parent
source = (b / 'audit-commercial-trace-046.py').read_text()
source = source.replace('reports/commercial-trace-audit-046', 'reports/commercial-render-audit-059').replace('commercial046/', 'commercial059/')
start = source.index('METHODS = [')
end = source.index('\n]\n', start) + 3
methods = [
    ('base', 'partial_mode_result', 'RSSystemProperties::GetUniPartialRenderEnabled()', '', False),
    ('service', 'screen_request_frame', 'DrawableV2::RSScreenRenderNodeDrawable::RequestFrame(', '', False),
    ('service', 'commit_layers', 'RSUniRenderComposerAdapter::CommitLayers(', '', False),
    ('service', 'screen_node_skip_result', 'DrawableV2::RSScreenRenderNodeDrawable::OnDraw(', '', False),
]
source = source[:start] + 'METHODS = ' + repr(methods) + source[end:]
source = source.replace('va = int(found[0][0], 16)',
                        "va = int(found[0][0], 16) + {'partial_mode_result': 0x68, 'screen_request_frame': 0, 'commit_layers': 0, 'screen_node_skip_result': 0x18d8}[event]")

if __name__ == '__main__':
    path = b.parent / 'reports/commercial-oneway-audit-045/base.so'
    text = subprocess.check_output(['llvm-objdump-19', '-d', '--demangle', '--start-address=0x692d80', '--stop-address=0x692d90', str(path)], text=True)
    assert '692d84:' in text and 'ConvertToInt' in text and '692d88:' in text
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
