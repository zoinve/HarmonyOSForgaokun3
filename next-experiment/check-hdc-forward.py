from pathlib import Path
import sys
base=Path(__file__).resolve().parent
number=next(n for n in range(9918,99999) if not (base/f'run-{n}').exists())
path=base/'run.py';text=path.read_text()
sys.argv=[str(path),str(number),'--virgl','--user-network','--hdc-port','18818']
scope={'__file__':str(path)}
exec(compile(text[:text.index("subprocess.run(['ssh', 'matebook', 'mkdir '")],str(path),'exec'),scope)
cmd=scope['c']['command']
assert cmd[cmd.index('-netdev')+1]=='user,id=normalnet,hostfwd=tcp:127.0.0.1:18818-10.0.2.15:8710'
assert '-accel' in cmd and 'kvm' in cmd
print('PASS: optional HDC ingress is host-loopback only; KVM preserved')
