from pathlib import Path
BASE=Path(__file__).resolve().parent
if __name__=='__main__':
 source=(BASE/'collect-radio-276-279.py').read_text()
 source=source.replace('commercial61-native-276','commercial61-native-321')
 source=source.replace('commercial-return-audit-276','commercial-return-audit-321').replace('279','324')
 source=source.replace(repr('266')+']',repr('266')+', '+', '.join(repr(x) for x in ['276','285','294','297','306'])+']')
 exec(compile(source,'collect-audio-321-324.generated.py','exec'),
      dict(__name__='__main__',__file__=str(BASE/'collect-audio-321-324.generated.py')))
