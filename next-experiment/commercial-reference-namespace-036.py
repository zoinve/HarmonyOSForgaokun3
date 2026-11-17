"""Keep L410 namespace implementation; omit Kirin/Mali-only preload providers."""
from pathlib import Path
import shlex,hashlib
REFERENCE=Path(__file__).resolve().parents[1]/'references/L410-HarmonyOS-Adaptations/graphics-namespace/l410-appspawn-r18-namespace-v1/appspawn_r18_namespace_exec.c'

def source():
    original=REFERENCE.read_text()
    start=original.index('static const char *kPreload =')
    end=original.index('\n\nint main(',start)
    # All namespace, privilege, failure and exec code stays reference-identical.
    return original[:start]+'static const char *kPreload = "libappspawn_helper.z.so";'+original[end:]

def launcher(original):
    assert original.count('\nexec ')==1
    argv=shlex.split(original.split('\nexec ',1)[1])
    assert argv[0]=='/system/bin/appspawn'
    assert '-mode appspawn' in argv and any('--sandbox-switch on' in a for a in argv)
    return '#!/system/bin/sh\nset -eu\nexec '+shlex.join([
        '/system/bin/aurora/appspawn-reference-namespace',
        '/vendor/lib64/passthrough',*argv])+'\n'

def provenance():
    return dict(reference_source=str(REFERENCE),reference_sha256=hashlib.sha256(REFERENCE.read_bytes()).hexdigest(),
                main_byte_identical=True,delta='Only preload list: original appspawn helper, no Kirin/Mali shims')
