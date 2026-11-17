from pathlib import Path
import runpy

BASE = Path(__file__).resolve().parent
source = runpy.run_path(str(BASE / 'analyze-commercial-input-response-105.py'))['source']
source = source.replace('commercial61-native-105', 'commercial61-native-107')
source = source.replace("else '105'", "else '107'").replace(
    "['075', '076', '077', '078', '099', '105']", "['075', '076', '077', '078', '099', '105', '107']")
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
