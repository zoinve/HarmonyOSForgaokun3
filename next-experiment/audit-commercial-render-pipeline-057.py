"""Audit original OnDraw branch reasons without dereferencing private objects."""
from pathlib import Path
import subprocess

b = Path(__file__).resolve().parent
source = (b / 'audit-commercial-trace-046.py').read_text()
source = source.replace('reports/commercial-trace-audit-046', 'reports/commercial-render-audit-057').replace('commercial046/', 'commercial057/')
start = source.index('METHODS = [')
end = source.index('\n]\n', start) + 3
events = {'screen_skip_reason': 0x41f3b4, 'screen_initial_gate': 0x41f240,
          'screen_missing_params': 0x41f250, 'screen_skip_result': 0x41f504}
methods = [('service', event, 'DrawableV2::RSScreenRenderNodeDrawable::OnDraw(', '', False) for event in events]
source = source[:start] + 'METHODS = ' + repr(methods) + source[end:]
source = source.replace('va = int(found[0][0], 16)',
                        'va = int(found[0][0], 16) + ' + repr({event: address - 0x41f104 for event, address in events.items()}) + '[event]')


def verify_branches():
    path = b.parent / 'reports/commercial-oneway-audit-045/service.so'
    checks = [('0x41f228', '0x41f278', ['cbz\tx21, 0x41f250', 'cbz\tx8, 0x41f250',
               'cbnz\tw8, 0x41f300', '41f244:', 'mov\tw9, #0x21', '41f25c:', 'mov\tw9, #0xc']),
              ('0x41f3a8', '0x41f3b8', ['41f3b4:', 'stlrb\tw9, [x8]']),
              ('0x41f4f4', '0x41f510', ['41f500:', 'CheckRenderSkipIfScreenOff', '41f504:', 'and\tw8, w0, #0x1'])]
    for start, end, needles in checks:
        text = subprocess.check_output(['llvm-objdump-19', '-d', '--no-show-raw-insn',
                                        '--start-address=' + start, '--stop-address=' + end, str(path)], text=True)
        for needle in needles:
            assert needle in text, needle


if __name__ == '__main__':
    verify_branches()
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
