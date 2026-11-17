from pathlib import Path
BASE=Path(__file__).resolve().parent
if __name__=='__main__':
 source=(BASE/'radio-workflow-295.py').read_text().replace('294','341').replace('285','331')
 source=source.replace('native Bluetooth entry diagnostics 341','native Bluetooth original discovery and ALSA 341')
 exec(compile(source,'bluetooth-workflow-342.generated.py','exec'),
   dict(__name__='__main__',__file__=str(BASE/'bluetooth-workflow-342.generated.py')))
