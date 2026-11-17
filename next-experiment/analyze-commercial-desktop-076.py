from pathlib import Path

b = Path(__file__).resolve().parent
source = (b / 'analyze-commercial-desktop-075.py').read_text().replace("else '075'", "else '076'").replace(
    "['074', '075']", "['074', '075', '076']").replace('COMMERCIAL075_SECOND_FULL_EXPORT', 'COMMERCIAL076_SECOND_FULL_EXPORT').replace(
    'COMMERCIAL075_START_RESULT', 'COMMERCIAL076_START_RESULT').replace('COMMERCIAL075_GUIDE_STOP_RESULT', 'COMMERCIAL076_GUIDE_STOP_RESULT').replace(
    'COMMERCIAL075_GUIDE_PID_RESULT', 'COMMERCIAL076_GUIDE_PID_RESULT').replace('COMMERCIAL075_SCENE_PID_RESULT', 'COMMERCIAL076_SCENE_PID_RESULT').replace(
    'COMMERCIAL075_COMMANDS_DONE', 'COMMERCIAL076_COMMANDS_DONE').replace('COMMERCIAL075_KEYBOARD ', 'COMMERCIAL076_KEYBOARD ')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
