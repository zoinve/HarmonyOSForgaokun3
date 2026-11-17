from pathlib import Path
BASE=Path(__file__).resolve().parent
if __name__=='__main__':
    source=(BASE/'radio-workflow-295.py').read_text().replace('294','401').replace('285','394')
    source=source.replace('native Bluetooth entry diagnostics 401','native real jack state and playback 401')
    exec(compile(source,'audio-workflow-402.generated.py','exec'),
        dict(__name__='__main__',__file__=str(BASE/'audio-workflow-402.generated.py')))
