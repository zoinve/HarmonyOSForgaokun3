from pathlib import Path

source = Path(__file__).with_name('audit-commercial-trace-046.py').read_text()
source = source.replace('reports/commercial-trace-audit-046', 'reports/commercial-render-audit-054').replace('commercial046/', 'commercial054/')
start = source.index('METHODS = [')
end = source.index('\n]\n', start) + 3
methods = [
    ('base', 'transaction_process', 'RSTransactionData::Process(', '', False),
    ('service', 'process_command', 'RSMainThread::ProcessCommand(', '', False),
    ('service', 'render', 'RSMainThread::Render(', '', False),
    ('service', 'uni_render', 'RSMainThread::UniRender(', '', False),
]
source = source[:start] + 'METHODS = ' + repr(methods) + source[end:]
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
