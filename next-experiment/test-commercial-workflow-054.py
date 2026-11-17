from pathlib import Path
import runpy

source = Path(__file__).with_name('test-commercial-workflow-050.py').read_text()
source = source.replace('commercial-workflow-050.py', 'commercial-workflow-054.py').replace('source050', 'source054').replace('commercial61-native-050', 'commercial61-native-054').replace('build-commercial-native-050.py', 'build-commercial-native-054.py').replace('COMMERCIAL050', 'COMMERCIAL054')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
