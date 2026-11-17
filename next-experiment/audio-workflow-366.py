from pathlib import Path
BASE=Path(__file__).resolve().parent
if __name__=='__main__':
 source=(BASE/'radio-workflow-295.py').read_text().replace('294','365').replace('285','353')
 source=source.replace('native Bluetooth entry diagnostics 365','native explicit audio routes and BLE 365')
 exec(compile(source,'audio-workflow-366.generated.py','exec'),
   dict(__name__='__main__',__file__=str(BASE/'audio-workflow-366.generated.py')))
