from pathlib import Path
BASE=Path(__file__).resolve().parent
if __name__=='__main__':
    source=(BASE/'compress-audio-logs-335.py').read_text()
    source=source.replace('audio-log-compression-335.json','audio-log-compression-427.json')
    source=source.replace("['321']","['420']")
    exec(compile(source,'compress-audio-logs-427.generated.py','exec'),
         dict(__name__='__main__',__file__=str(BASE/'compress-audio-logs-427.generated.py')))
