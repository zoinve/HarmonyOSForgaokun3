from pathlib import Path
BASE=Path(__file__).resolve().parent
if __name__=='__main__':
    source=(BASE/'radio-workflow-295.py').read_text().replace('294','385').replace('285','378')
    source=source.replace('native Bluetooth entry diagnostics 385','native corrected real jack detection 385')
    exec(compile(source,'audio-workflow-386.generated.py','exec'),
        dict(__name__='__main__',__file__=str(BASE/'audio-workflow-386.generated.py')))
