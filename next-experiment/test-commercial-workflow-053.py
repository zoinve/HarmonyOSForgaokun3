from pathlib import Path
import runpy

source = Path(__file__).with_name('test-commercial-workflow-050.py').read_text()
source = source.replace('commercial-workflow-050.py', 'commercial-workflow-053.py').replace('source050', 'source053').replace('commercial61-native-050', 'commercial61-native-053').replace('build-commercial-native-050.py', 'build-commercial-native-053.py').replace('COMMERCIAL050', 'COMMERCIAL053')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
