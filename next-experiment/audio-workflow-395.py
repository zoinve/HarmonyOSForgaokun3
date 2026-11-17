from pathlib import Path
BASE=Path(__file__).resolve().parent
if __name__=='__main__':
    source=(BASE/'radio-workflow-295.py').read_text().replace('294','394').replace('285','385')
    source=source.replace('native Bluetooth entry diagnostics 394','native final-overlay jack detection 394')
    exec(compile(source,'audio-workflow-395.generated.py','exec'),
        dict(__name__='__main__',__file__=str(BASE/'audio-workflow-395.generated.py')))
