from pathlib import Path
BASE=Path(__file__).resolve().parent
if __name__=='__main__':
 source=(BASE/'radio-workflow-295.py').read_text().replace('294','321').replace('285','306')
 source=source.replace('native Bluetooth entry diagnostics 321','native Bluetooth and acknowledged ALSA audio 321')
 exec(compile(source,'audio-workflow-322.generated.py','exec'),
      dict(__name__='__main__',__file__=str(BASE/'audio-workflow-322.generated.py')))
