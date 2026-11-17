"""Handle repeated efibootmgr verbose detail rows without exporting their text."""
from pathlib import Path

BASE=Path(__file__).resolve().parent

if __name__=='__main__':
    source=(BASE/'inspect-boot-preservation-175.py').read_text()
    old='''def rows(text):
 result={}
 for line in text.splitlines():
  key=line.split(':',1)[0]
  entry=re.match(r'^(Boot[0-9A-Fa-f]{4})\\*?',line)
  if entry:key=entry[1]
  assert key not in result
  result[key]=line
 return result'''
    new='''def rows(text):
 grouped={}
 for line in text.splitlines():
  key='OtherOutput'
  entry=re.match(r'^(Boot[0-9A-Fa-f]{4})\\*?',line)
  if entry:key=entry[1]
  elif line.partition(':')[0] in ['BootCurrent','BootOrder','Timeout']:key=line.partition(':')[0]
  grouped.setdefault(key,[]).append(line)
 return {key:'\\n'.join(lines) for key,lines in grouped.items()}'''
    assert source.count(old)==1
    source=source.replace(old,new,1).replace('preservation-difference-inspection','preservation-difference-inspection-v2')
    exec(compile(source,'inspect-boot-preservation-175-v2.generated.py','exec'),
         {'__name__':'__main__','__file__':str(BASE/'inspect-boot-preservation-175-v2.generated.py')})
