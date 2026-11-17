"""Separate kernel policy evidence, original reader errors, and UI acceptance."""
from pathlib import Path
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
READER = runpy.run_path(str(ROOT / 'next-experiment/compress-historical-logs-226.py'))['open_log']


def phase_inspect(stream):
    active = False
    policy = None
    attribute = None
    policies = {}
    statuses = []
    deferred = []
    service_samples = []
    for index, raw in enumerate(stream, 1):
        line = raw.decode(errors='replace').strip()
        match = re.fullmatch(r'PHASE_END cpufreq-icc-provider-471 status=(\d+)', line)
        if match:
            statuses.append(int(match[1]))
        if 'qcom-cpufreq-hw: Failed to find icc paths' in line:
            deferred.append(index)
        if line == 'CPUFREQ471_BEGIN_REAL_SYSFS':
            active = True
            continue
        if line == 'CPUFREQ471_END_NOT_TASK_MANAGER_ACCEPTANCE':
            active = False
        if active:
            match = re.fullmatch(r'POLICY=/sys/devices/system/cpu/cpufreq/(policy\d+)', line)
            if match:
                policy = match[1]
                policies[policy] = {}
                attribute = None
            elif line.startswith('ATTRIBUTE='):
                attribute = line[len('ATTRIBUTE='):]
            elif policy and attribute:
                if attribute == 'scaling_driver' and line == 'qcom-cpufreq-hw':
                    policies[policy][attribute] = line
                elif attribute == 'related_cpus' and re.fullmatch(r'\d+(?: \d+)*', line):
                    policies[policy][attribute] = [int(value) for value in line.split()]
                elif attribute in ('scaling_cur_freq', 'scaling_min_freq', 'scaling_max_freq') and line.isdigit():
                    policies[policy][attribute] = int(line)
                attribute = None
        match = re.fullmatch(r'cpu(\d+), cpuFreq=(\d+), minFreq=(\d+), maxFreq=(\d+)', line)
        if match:
            values = [int(value) for value in match.groups()]
            service_samples.append(dict(line=index, cpu=values[0], current=values[1], minimum=values[2], maximum=values[3]))
    valid = {name:row for name,row in policies.items()
             if row.get('scaling_driver') == 'qcom-cpufreq-hw' and row.get('related_cpus')
             and all(row.get(key, 0) > 0 for key in ('scaling_cur_freq', 'scaling_min_freq', 'scaling_max_freq'))}
    return dict(provider_load_statuses=statuses, policies=policies, complete_policy_names=sorted(valid),
                missing_icc_deferred_probe_lines=deferred, original_cpu_service_samples=service_samples,
                real_native_cpufreq_policies_observed=bool(valid), task_manager_ui_verified=False,
                nominal_or_host_frequency_substituted=False)


def reader_inspect(stream):
    errors = []
    for index, raw in enumerate(stream, 1):
        line = raw.decode(errors='replace')
        if 'GetIntegerFromFile' in line and 'failed to get content' in line:
            match = re.search(r'/sys/devices/system/cpu/(cpu\d+)/cpufreq/(scaling_cur_freq|scaling_min_freq|scaling_max_freq)', line)
            if match:
                errors.append(dict(line=index, cpu=match[1], attribute=match[2]))
    return dict(original_frequency_reader_error_count=len(errors), original_frequency_reader_errors=errors,
                absence_of_reader_error_not_ui_success=True)


if __name__ == '__main__':
    report = ROOT / 'reports/commercial61-native-471'
    output = report / 'cpufreq-analysis-484.json'
    assert not output.exists()
    manifest = json.loads((report / 'runtime-evidence/retrieval-manifest.json').read_text())
    phases = [name for name in manifest['files'] if re.fullmatch(r'phase-\d+\.log', name)]
    assert phases
    phase = max(phases, key=lambda name: int(re.search(r'\d+', name)[0]))
    with READER(report / 'runtime-evidence/raw' / phase) as stream:
        result = phase_inspect(stream)
    with READER(report / 'runtime-evidence/raw/interactive-hilog030.log') as stream:
        result.update(reader_inspect(stream))
    result.update(run=manifest['run'], phase_file=phase)
    output.open('x').write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
