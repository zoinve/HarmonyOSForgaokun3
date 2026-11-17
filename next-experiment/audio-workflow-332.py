from pathlib import Path
BASE=Path(__file__).resolve().parent
if __name__=='__main__':
 source=(BASE/'radio-workflow-295.py').read_text().replace('294','331').replace('285','321')
 source=source.replace('native Bluetooth entry diagnostics 331','native Bluetooth and idle-safe ALSA audio 331')
 exec(compile(source,'audio-workflow-332.generated.py','exec'),
   dict(__name__='__main__',__file__=str(BASE/'audio-workflow-332.generated.py')))
