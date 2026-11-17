from pathlib import Path

source = Path(__file__).with_name('analyze-commercial-trace-046.py').read_text()
source = source.replace('commercial61-native-046', 'commercial61-native-047').replace('COMMERCIAL046', 'COMMERCIAL047')
exec(compile(source, __file__, 'exec'), globals())
