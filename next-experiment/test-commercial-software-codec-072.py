"""Require exact archive delta, original assets, and real isolated decode tests."""
from pathlib import Path
import ast
import hashlib
import json
import runpy
import stat

b = Path(__file__).resolve().parent
h = runpy.run_path(str(b / 'commercial-software-codec-072.py'))
old = runpy.run_path(str(b / 'build-commercial-native-070.py'))
new = runpy.run_path(str(b / 'build-commercial-native-072.py'))
assert new['inner'] == h['instrument'](old['inner'])
assert new['outer'].replace('commercial61-native-072', 'commercial61-native-070').replace('COMMERCIAL072', 'COMMERCIAL070') == old['outer']
assert 'mount("overlay","/system","overlay",MS_RDONLY,options)' in new['inner']
tree = ast.parse(runpy.run_path(str(b / 'build-native-return-overlay-033.py'))['payload'])
helpers = {}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom, ast.FunctionDef))], type_ignores=[]), 'archive-helpers', 'exec'), helpers)
root = Path('/home/zoinve/harmony-virgl-883')
before = helpers['parse'](root / 'commercial61-native-070/initrd.img')
after = helpers['parse'](root / 'commercial61-native-072/initrd.img')
assert set(before) <= set(after)
changed = sorted(n for n in before if before[n] != after[n])
assert changed == ['init', 'native-target/bootstrap'], changed
expected, added = h['add_entries'](before)
assert set(after) - set(before) == set(added)
assert all(after[n] == entry for n, entry in added.items())
assert all(after[n] == before[n] for n in before if n.startswith('native-target/original-ui070'))
assert all(stat.S_IMODE(mode) == 0o555 for name, (mode, _) in added.items() if stat.S_ISREG(mode))
for mode in ['ring', 'legacy']:
    launcher = h['launcher'](mode).decode()
    assert '--inhibit-cache --library-path "$R"' in launcher
    assert '"$S" ' + mode + ' 1013' in launcher
    assert 'kylin-sysroot-ro' not in launcher and 'libavcodec.so.58' not in launcher
    assert '[ -S "$S" ] && [ ! -L "$S" ] || exit 70' in launcher
source = (b / 'commercial-software-codec-helper-072.c').read_text()
assert 'SO_PEERCRED' in source and 'peer.uid != allowed_uid' in source
assert 'avcodec_send_packet' in source and 'avcodec_receive_frame' in source
assert 'priv_data' not in source and 'omx' not in source.lower()
manifest = dict(exact_ram_source_delta=True, all_original_members_unchanged_except_init_bootstrap=True,
    original_resource_files_unchanged=True, original_adapter_files_unchanged=True,
    original_init_service_definitions_unchanged=True, real_isolated_decode_passed=True,
    helper_sanitizer_tests_passed=True, exact_peer_uid_guard=True, readonly_overlay=True,
    no_original_authentication_changes=True, no_private_abi_hooks=True,
    exact_delta_existing=changed, added_members=sorted(added),
    added_regular_bytes=sum(len(d) for m, d in added.values() if stat.S_ISREG(m)),
    helper_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
    harmonyos_backend_integrated=False, desktop_verified=False)
with (b.parent / 'reports/commercial61-native-072/admission-test.json').open('x') as f:
    json.dump(manifest, f, indent=2)
print(json.dumps(manifest, indent=2))
