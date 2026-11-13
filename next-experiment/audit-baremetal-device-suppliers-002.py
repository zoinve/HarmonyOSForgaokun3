"""Read-only supplier graph from running Ubuntu; never load candidate modules."""
from pathlib import Path
import json
import subprocess

report = Path(__file__).resolve().parent.parent / 'reports/baremetal-device-suppliers-002.json'
assert not report.exists()
payload = r'''
from pathlib import Path
import collections,json,subprocess
mount=subprocess.check_output(['findmnt','-n','-o','SOURCE,UUID','--target','/mnt/harmony-lab'],text=True).split()
assert mount==['/dev/nvme0n1p4','00029cdd-1748-4d2f-b73b-8e8164922098']
module_root=Path('/mnt/harmony-lab/work/native-module-root-001')
release='7.1.0-rc3-gaokun3-el2'
assert (module_root/'lib/modules'/release/'modules.dep').is_file()
seeds={Path('/sys/class/block/nvme0n1/device').resolve()}
for bus in ['platform','i2c','spi']:
 for device in (Path('/sys/bus')/bus/'devices').iterdir():
  driver=device/'driver'
  if driver.exists() and any(key in driver.resolve().name.lower() for key in ['msm','dsi','himax','gaokun','i2c_hid','i2c-hid']):
   seeds.add(device.resolve())
for device in Path('/sys/class/input').glob('event*/device'):
 seeds.add(device.resolve())
queue=collections.deque(sorted(seeds)); visited={}; edges=[]
while queue:
 node=queue.popleft()
 if str(node) in visited:continue
 assert len(visited)<1024,'Supplier graph exceeded bounded audit size'
 driver=node/'driver'; module=driver/'module'; alias=node/'modalias'
 row=dict(path=str(node),driver=driver.resolve().name if driver.exists() else None,
          running_module=module.resolve().name if module.exists() else None,
          modalias=alias.read_text().strip() if alias.is_file() else None)
 visited[str(node)]=row
 for parent in node.parents:
  if str(parent)=='/sys/devices':break
  if not str(parent).startswith('/sys/devices/'):break
  if (parent/'driver').exists():
   edges.append(dict(consumer=str(node),supplier=str(parent),kind='parent'))
   queue.append(parent);break
 for link in node.glob('supplier:*'):
  target=(link.resolve()/'supplier').resolve()
  if target.exists() and str(target).startswith('/sys/devices/'):
   edges.append(dict(consumer=str(node),supplier=str(target),kind='device_link'))
   queue.append(target)
module_names=sorted({r['running_module'] for r in visited.values() if r['running_module']})
checks=[]
for module in module_names:
 args=['/usr/sbin/modprobe','--dirname',str(module_root),'--set-version',release,
       '--config',str(module_root/'etc/modprobe.d'),'--show-depends',module]
 # modprobe path is discovered without depending on root's PATH.
 if not Path(args[0]).is_file():args[0]='/usr/bin/kmod';args.insert(1,'modprobe')
 p=subprocess.run(args,text=True,capture_output=True,timeout=10)
 checks.append(dict(module=module,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr))
print(json.dumps(dict(seeds=sorted(map(str,seeds)),nodes=list(visited.values()),edges=edges,
 candidate_release=release,candidate_module_checks=checks,
 scope='Running Ubuntu supplier evidence and offline candidate dependency resolution only',
 modules_loaded=False,boot_entries_modified=False,native_boot_attempted=False),indent=2))
'''
p = subprocess.run(['ssh', 'matebook', 'python3 -'], input=payload, text=True,
                   capture_output=True, timeout=180)
p.check_returncode()
result = json.loads(p.stdout)
report.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(dict(nodes=len(result['nodes']), edges=len(result['edges']),
                     modules_checked=len(result['candidate_module_checks']),
                     unresolved=[c['module'] for c in result['candidate_module_checks'] if c['returncode']],
                     modules_loaded=False), indent=2))
