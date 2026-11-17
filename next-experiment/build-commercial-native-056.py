from pathlib import Path

source = Path(__file__).with_name('build-commercial-native-054.py').read_text().replace('054', '056')
exec(compile(source, __file__, 'exec'), globals())
