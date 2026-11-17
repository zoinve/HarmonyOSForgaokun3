"""Audit actual intermediate frame/dirty skip and processor failure branches."""
from pathlib import Path
import subprocess

b = Path(__file__).resolve().parent
source = (b / 'audit-commercial-trace-046.py').read_text()
source = source.replace('reports/commercial-trace-audit-046', 'reports/commercial-render-audit-058').replace('commercial046/', 'commercial058/')
start = source.index('METHODS = [')
end = source.index('\n]\n', start) + 3
events = {'frame_skip_result': 0x41f8e8, 'screen_node_skip_result': 0x4209dc,
          'processor_create_failed': 0x41fd2c, 'processor_init_failed': 0x4205e8}
methods = [('service', event, 'DrawableV2::RSScreenRenderNodeDrawable::OnDraw(', '', False) for event in events]
source = source[:start] + 'METHODS = ' + repr(methods) + source[end:]
source = source.replace('va = int(found[0][0], 16)',
                        'va = int(found[0][0], 16) + ' + repr({event: address - 0x41f104 for event, address in events.items()}) + '[event]')


def verify_branches():
    path = b.parent / 'reports/commercial-oneway-audit-045/service.so'
    checks = [('0x41f8d8', '0x41f8f0', ['41f8e4:', 'SkipFrame', '41f8e8:', '41f8ec:', 'mov\tw20, w0']),
              ('0x4209cc', '0x4209e4', ['4209d8:', 'CheckScreenNodeSkip', '4209dc:', 'mov\tw24, w0']),
              ('0x41fd08', '0x41fd30', ['41fd0c:', 'mov\tw9, #0x10', '41fd2c:', 'stlrb\tw9, [x8]']),
              ('0x4205dc', '0x4205ec', ['tbnz\tw22, #0x0, 0x41fe84', '4205e4:', 'mov\tw9, #0x6', '4205e8:', 'stlrb\tw9, [x8]'])]
    for start, end, needles in checks:
        text = subprocess.check_output(['llvm-objdump-19', '-d', '--no-show-raw-insn',
                                        '--start-address=' + start, '--stop-address=' + end, str(path)], text=True)
        for needle in needles:
            assert needle in text, needle


if __name__ == '__main__':
    verify_branches()
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
