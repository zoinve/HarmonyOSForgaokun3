from pathlib import Path

source = Path(__file__).with_name('commercial-workflow-059.py').read_text().replace('059', '061')
exec(compile(source, __file__, 'exec'), globals())
