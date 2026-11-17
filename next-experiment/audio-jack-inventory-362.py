from pathlib import Path
BASE=Path(__file__).resolve().parent
if __name__=='__main__':
 source=(BASE/'audio-jack-inventory-361.py').read_text()
 source=source.replace('audio-jack-inventory-361.json','audio-jack-inventory-362.json')
 anchor="'cget','name='+name"
 assert source.count(anchor)==1
 source=source.replace(anchor,"'cget','iface=CARD,name='+name")
 exec(compile(source,'audio-jack-inventory-362.generated.py','exec'),
   dict(__name__='__main__',__file__=str(BASE/'audio-jack-inventory-362.generated.py')))
