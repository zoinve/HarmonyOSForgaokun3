from pathlib import Path
BASE=Path(__file__).resolve().parent
if __name__=='__main__':
    source=(BASE/'radio-workflow-295.py').read_text().replace('294','378').replace('285','365')
    source=source.replace('native Bluetooth entry diagnostics 378','native real jack detection and audio 378')
    exec(compile(source,'audio-workflow-379.generated.py','exec'),
        dict(__name__='__main__',__file__=str(BASE/'audio-workflow-379.generated.py')))
