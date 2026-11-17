from pathlib import Path

source = Path(__file__).with_name('build-commercial-native-057.py').read_text().replace('057', '058')
exec(compile(source, __file__, 'exec'), globals())
