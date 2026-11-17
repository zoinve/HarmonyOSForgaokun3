from pathlib import Path
import json
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if __name__ == '__main__':
    output = ROOT / 'reports/touch-monitor-test-304.json'
    assert not output.exists()
    source = ROOT / 'next-experiment/native-touch-monitor-303.c'
    with tempfile.TemporaryDirectory(prefix='touch304-') as directory:
        binary = Path(directory) / 'monitor'
        subprocess.run(['gcc', '-O2', '-Wall', '-Wextra', '-Werror',
                        '-fsanitize=address,undefined', str(source), '-o', str(binary)], check=True)
        result = subprocess.run([str(binary), '--self-test'], capture_output=True, text=True, check=True)
        assert 'passed=1' in result.stdout
        target = Path(directory) / 'monitor-arm64'
        subprocess.run(['aarch64-linux-gnu-gcc', '-static', '-O2', '-Wall', '-Wextra', '-Werror',
                        str(source), '-o', str(target)], check=True)
    evidence = dict(parser_test_passed=True, sanitizers=['address','undefined'],
        arm64_static_build_passed=True, target_executed=False,
        physical_multitouch_verified=False, original_mmi_modified=False,
        tested=['two simultaneous contacts','contact release','invalid slot','SYN_DROPPED invalidation'])
    output.open('x').write(json.dumps(evidence, indent=2))
    print(json.dumps(evidence, indent=2))
