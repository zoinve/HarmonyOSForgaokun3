"""Read two already-working device firmware files; stage copies only in WSL."""
import subprocess,json,hashlib
remote="""
from pathlib import Path
import hashlib,base64,json
names=['wcnhpbtfw21.tlv','wcnhpnv21g.bin']
out=[]
for name in names:
 p=Path('/usr/lib/firmware/qca')/name
 b=p.read_bytes()
 out.append(dict(name=name,source=str(p),sha256=hashlib.sha256(b).hexdigest(),data=base64.b64encode(b).decode()))
print(json.dumps(out))
"""
r=subprocess.run(['ssh','matebook','python3','-'],input=remote,text=True,capture_output=True,check=True,timeout=30)
rows=json.loads(r.stdout)
expected=['77d8979da5c613c85550549dcef8fb8ec6fe2e5576942855ea03179a11597c1f','1e2fd8954f88a8133b17a04c802f816fe1be2ca856fd60d620359f568c511fbf']
assert [x['sha256'] for x in rows]==expected
script="""
from pathlib import Path
import base64,hashlib,json
rows=ROWS
root=Path('/home/zoinve/harmony-virgl-883/native-qca-firmware-021')
root.mkdir(exist_ok=False)
for row in rows:
 b=base64.b64decode(row['data'],validate=True)
 assert hashlib.sha256(b).hexdigest()==row['sha256']
 with (root/row['name']).open('xb') as f:f.write(b)
 row.pop('data');row['bytes']=len(b)
with (root/'result.json').open('x') as f:json.dump(rows,f,indent=2)
print(json.dumps(rows,indent=2))
""".replace('ROWS',repr(rows))
subprocess.run(['wsl','-d','Debian','--','python3','-'],input=script,text=True,check=True)
