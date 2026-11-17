from pathlib import Path
BASE=Path(__file__).resolve().parent
if __name__=='__main__':
    source=(BASE/'analyze-audio-398.py').read_text()
    source=source.replace(".replace('385','394')",".replace('385','401')")
    source=source.replace('audio-analysis-398.json','audio-analysis-405.json')
    exec(compile(source,'analyze-audio-405.generated.py','exec'),
        dict(__name__='__main__',__file__=str(BASE/'analyze-audio-405.generated.py')))
