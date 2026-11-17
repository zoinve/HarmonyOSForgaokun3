"""Executable static/source checks, explicitly not native compilation evidence."""
from pathlib import Path
import hashlib
import json
import runpy

b = Path(__file__).resolve().parent
report = b.parent / 'reports/commercial-allocator-source-test-073-r2'
report.mkdir()
h = runpy.run_path(str(b / 'commercial-allocator-observer-073.py'))
p = runpy.run_path(str(b / 'build-commercial-native-072.py'))
n = runpy.run_path(str(b / 'build-commercial-native-073.py'))
reference = Path('C:/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports/graphics/buffer_vdi.cpp')
if not reference.exists():
    reference = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports/graphics/buffer_vdi.cpp')
original = reference.read_text()
observed = h['allocator'](original)
restored = observed.replace('#include <cerrno>\n#include <atomic>', '#include <cerrno>', 1)
restored = restored.replace(h['LOGGER'] + '\n', '', 1)
restored = restored.replace('        out = nullptr;\n        allocator073_request(info);', '        out = nullptr;', 1)
assert restored == original, 'unexpected allocator behavioral source delta'
assert n['inner'] == h['inner'](p['inner'])
for function, source in [(h['allocator'], observed), (h['inner'], n['inner'])]:
    try:
        function(source)
    except AssertionError:
        pass
    else:
        raise AssertionError('duplicate instrumentation was accepted')
names = ['commercial-allocator-observer-073.py', 'build-commercial-allocator-073.py',
    'test-commercial-allocator-logger-073.py', 'build-commercial-native-073.py',
    'build-commercial-overlay-073.py', 'commercial-workflow-073.py',
    'retain-commercial-entries-073.py', 'test-commercial-allocator-admission-073.py',
    'test-commercial-allocator-source-073.py']
for name in names:
    compile((b / name).read_text(), str(b / name), 'exec')
for forbidden in ['process_vm_readv', '/mem', 'PTRACE_PEEK', 'PTRACE_POKE']:
    assert forbidden not in h['INVENTORY']
workflow = runpy.run_path(str(b / 'commercial-workflow-073.py'))
parent = json.loads((b.parent / 'reports/commercial61-native-072/overlay-result-xz.json').read_text())
for action in ['install-commercial-native', 'run-commercial-native',
               'retrieve-commercial-evidence', 'verify-commercial-return']:
    source = workflow['transform073'](workflow['previous']['source072'](action), action)
    compile(source, 'generated-' + action, 'exec')
    if action == 'install-commercial-native':
        assert source.count("'initrd /commercial61-native-072/initrd.img','initrd /commercial61-native-073/initrd.img'") == 1
        assert "assert sha(esp/'commercial61-native-072/initrd.img')==" + repr(parent['sha256']) in source
        assert "'ordered_chain_equals_full_073'" in source
        assert "report/'installation-result.json'" in source
try:
    workflow['source073']('install-commercial-native')
except FileNotFoundError:
    pass
else:
    raise AssertionError('unexpected successful admission before native tests')
result = dict(exact_reversible_allocator_logging_delta=True, exact_native_source_injection=True,
    duplicate_instrumentation_rejected=True, public_process_metadata_only=True,
    python_syntax_files=len(names), generated_workflow_sources_compile=True,
    generated_install_requires_exact_072_parent_hash=True,
    generated_boot_entry_includes_072_before_073=True, install_refused_without_native_admission=True,
    reference_source_sha256=hashlib.sha256(reference.read_bytes()).hexdigest(),
    observer_module_sha256=hashlib.sha256((b / 'commercial-allocator-observer-073.py').read_bytes()).hexdigest(),
    source_only=True, cpp_compilation_verified=False, logger_runtime_verified=False,
    native_boot_requested=False, desktop_verified=False)
with (report / 'result.json').open('x') as f:
    json.dump(result, f, indent=2)
print(json.dumps(result, indent=2))
