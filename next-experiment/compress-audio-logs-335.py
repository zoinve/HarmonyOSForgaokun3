from pathlib import Path
BASE=Path(__file__).resolve().parent
if __name__=='__main__':
 source=(BASE/'compress-radio-logs-282.py').read_text()
 source=source.replace('radio-log-compression-282.json','audio-log-compression-335.json')
 source=source.replace("['253', '262', '266']","['321']")
 exec(compile(source,'compress-audio-logs-335.generated.py','exec'),
   dict(__name__='__main__',__file__=str(BASE/'compress-audio-logs-335.generated.py')))
