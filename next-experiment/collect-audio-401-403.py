from pathlib import Path
BASE=Path(__file__).resolve().parent
if __name__=='__main__':
    source=(BASE/'collect-radio-276-279.py').read_text()
    source=source.replace('commercial61-native-276','commercial61-native-401')
    source=source.replace('commercial-return-audit-276','commercial-return-audit-401').replace('279','403')
    source=source.replace(repr('266')+']',repr('266')+', '+', '.join(repr(x) for x in
        ['276','285','294','297','306','321','331','341','353','365','378','385','394'])+']')
    exec(compile(source,'collect-audio-401-403.generated.py','exec'),
        dict(__name__='__main__',__file__=str(BASE/'collect-audio-401-403.generated.py')))
