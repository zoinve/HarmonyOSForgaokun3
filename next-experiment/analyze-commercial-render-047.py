from pathlib import Path

source = Path(__file__).with_name('analyze-commercial-render-045.py').read_text()
source = source.replace('commercial61-native-045', 'commercial61-native-047')
exec(compile(source, __file__, 'exec'), globals())
