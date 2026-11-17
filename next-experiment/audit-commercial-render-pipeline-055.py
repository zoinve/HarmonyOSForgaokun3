"""Resolve original instructions at actual command execution and worker handoff."""
from pathlib import Path
import subprocess

b = Path(__file__).resolve().parent
source = (b / 'audit-commercial-trace-046.py').read_text()
source = source.replace('reports/commercial-trace-audit-046', 'reports/commercial-render-audit-055').replace('commercial046/', 'commercial055/')
start = source.index('METHODS = [')
end = source.index('\n]\n', start) + 3
methods = [
    ('base', 'command_execute', 'RSTransactionData::Process(', '', False),
    ('service', 'screen_skip_result', 'RSMainThread::UniRender(', '', False),
    ('service', 'worker_sync', 'RSUniRenderThread::Sync(', '', False),
    ('service', 'worker_render', 'RSUniRenderThread::Render(', '', False),
]
source = source[:start] + 'METHODS = ' + repr(methods) + source[end:]
source = source.replace("va = int(found[0][0], 16)",
                        "va = int(found[0][0], 16) + {'command_execute': 0x5c, 'screen_skip_result': 0x2a8}.get(event, 0)")


def verify_internal_sites():
    root = b.parent / 'reports/commercial-oneway-audit-045'
    checks = [('base.so', '0x5e8948', '0x5e8960', ['5e8954:', 'ldr', '[x8, #0x18]', '5e8958:', 'blr\tx8']),
              ('service.so', '0x1945cc', '0x1945ec', ['1945e4:', 'CheckRenderSkipIfScreenOff', '1945e8:', 'tbnz\tw0, #0x0'])]
    for name, start, end, needles in checks:
        text = subprocess.check_output(['llvm-objdump-19', '-d', '--no-show-raw-insn',
                                        '--start-address=' + start, '--stop-address=' + end,
                                        str(root / name)], text=True)
        for needle in needles:
            assert needle in text, (name, needle)


if __name__ == '__main__':
    verify_internal_sites()
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
