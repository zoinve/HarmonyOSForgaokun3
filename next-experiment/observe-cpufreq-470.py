"""Read Ubuntu cpufreq availability after458 returns; never set frequency."""
from pathlib import Path
import json
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REMOTE = r'''
from pathlib import Path
import datetime,json,platform,re,stat,time
def read(path):
 try:
  with path.open() as stream:value=stream.read(4096).strip()
  return dict(value=value,mode=oct(stat.S_IMODE(path.stat().st_mode)))
 except OSError as error:return dict(error=error.errno)
root=Path('/sys/devices/system/cpu')
policies=sorted((p for p in (root/'cpufreq').glob('policy*') if re.fullmatch(r'policy\d+',p.name)),key=lambda p:int(p.name[6:]))
attributes=['scaling_driver','scaling_governor','affected_cpus','related_cpus',
 'cpuinfo_min_freq','cpuinfo_max_freq','cpuinfo_cur_freq','scaling_min_freq',
 'scaling_max_freq','scaling_cur_freq','scaling_available_frequencies']
inventory={p.name:{name:read(p/name) for name in attributes} for p in policies}
cpu_links={p.name:dict(cpufreq_exists=(p/'cpufreq').exists(),online=read(p/'online'))
 for p in sorted(root.glob('cpu[0-9]*')) if re.fullmatch(r'cpu\d+',p.name)}
samples=[]
for index in range(5):
 samples.append(dict(monotonic_ns=time.monotonic_ns(),policies={p.name:{name:read(p/name)
  for name in ['scaling_cur_freq','cpuinfo_cur_freq']} for p in policies}))
 if index<4:time.sleep(0.2)
print(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),kernel=platform.release(),
 context='Ubuntu host only, not HarmonyOS service or UI acceptance',policies=inventory,
 cpu_links=cpu_links,samples=samples,frequency_or_governor_written=False,
 workload_or_stress_started=False,missing_values_fabricated=False),indent=2))
'''
if __name__ == '__main__':
    report = ROOT / 'reports/commercial61-native-458'
    output = report / 'cpufreq-host-observation-470.json'
    assert not output.exists()
    observed = json.loads((report / 'boot-observation-462.json').read_text())
    assert observed['returned']
    ssh = runpy.run_path(str(ROOT / 'next-experiment/deploy-settings-data-198.py'))['SSH']
    proc = subprocess.run(ssh + ['sudo -n python3 -'], input=REMOTE, text=True,
                          capture_output=True, timeout=25)
    assert proc.returncode == 0, proc.stderr
    result = json.loads(proc.stdout)
    assert result['boot_id'] == observed['ubuntu']['boot_id']
    output.open('x').write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(boot_id=result['boot_id'],policies=result['policies'],
                         host_only=True,frequency_written=False), indent=2))
