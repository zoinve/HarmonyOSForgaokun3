from pathlib import Path

source = Path(__file__).with_name('test-commercial-trace-analysis-046.py').read_text()
source = source.replace('analyze-commercial-trace-046.py', 'analyze-commercial-trace-047.py')
exec(compile(source, __file__, 'exec'), globals())
