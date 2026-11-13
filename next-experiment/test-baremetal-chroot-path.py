"""Exercise the packager's actual chroot selection without packaging or mounting."""
from pathlib import Path
import ast
import subprocess
import sys

path = Path(sys.argv[1]).resolve()
source = path.read_text()
if "exec(compile(source," in source:
    namespace = {'__file__': str(path)}
    exec(source[:source.index('exec(compile(source,')], namespace)
    source = namespace['source']
tree = ast.parse(source)
payload = next(n.value.value for n in tree.body if isinstance(n, ast.Assign)
               and any(isinstance(x, ast.Name) and x.id == 'payload' for x in n.targets))
tree = ast.parse(payload)
call = next(n for n in ast.walk(tree) if isinstance(n, ast.Call)
            and isinstance(n.func, ast.Attribute) and n.func.attr == 'run'
            and n.args and isinstance(n.args[0], ast.BinOp)
            and isinstance(n.args[0].left, ast.List))
choice = call.args[0].left.elts[0]
if isinstance(choice, ast.Name):
    choice = next(n.value for n in tree.body if isinstance(n, ast.Assign)
                  and any(isinstance(x, ast.Name) and x.id == choice.id for x in n.targets))
expression = ast.unparse(choice)
probe = """
import os,shutil,subprocess
p=EXPRESSION
assert p and os.path.isfile(p) and os.access(p,os.X_OK), 'chroot selection is not an executable: '+repr(p)
r=subprocess.run([p,'--version'],capture_output=True,text=True,check=True)
assert 'chroot' in r.stdout
print('PASS: actual chroot selection executes --version:',p)
""".replace('EXPRESSION', expression)
r = subprocess.run(['ssh', 'matebook', 'sudo -n python3 -'], input=probe,
                   text=True, capture_output=True, timeout=30)
print(r.stdout, end='')
print(r.stderr, end='')
sys.exit(r.returncode)
