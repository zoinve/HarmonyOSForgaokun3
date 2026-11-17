from pathlib import Path
BASE=Path(__file__).resolve().parent
if __name__=='__main__':
 source=(BASE/'build-audio-native-321.py').read_text().replace('321','331')
 exec(compile(source,'build-audio-native-331.generated.py','exec'),
   dict(__name__='__main__',__file__=str(BASE/'build-audio-native-331.generated.py')))
