from pathlib import Path
BASE=Path(__file__).resolve().parent
if __name__=='__main__':
 source=(BASE/'radio-workflow-295.py').read_text().replace('294','353').replace('285','341')
 source=source.replace('native Bluetooth entry diagnostics 353','native OHAudio nonzero playback and BLE 353')
 exec(compile(source,'audio-workflow-354.generated.py','exec'),
   dict(__name__='__main__',__file__=str(BASE/'audio-workflow-354.generated.py')))
