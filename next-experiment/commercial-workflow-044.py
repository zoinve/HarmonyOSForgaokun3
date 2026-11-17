"""Reuse completed workflow guards without changing hashes or global SSH config."""
from pathlib import Path
import runpy

previous = runpy.run_path(str(Path(__file__).with_name('commercial-workflow-043.py')))
configure_local_transport = previous['configure_local_transport']


def source044(name):
    text = previous['source043'](name)
    for old, new in [('commercial61-native-043', 'commercial61-native-044'),
                     ('commercial-return-audit-043', 'commercial-return-audit-044'),
                     ('COMMERCIAL043', 'COMMERCIAL044'),
                     ('ordered_chain_equals_full_043', 'ordered_chain_equals_full_044'),
                     ('libcommercial_rs_observer043.so', 'libcommercial_rs_observer044.so'),
                     ('Actual original Binder delivery 043', 'Original tokenless Binder delivery 044')]:
        text = text.replace(old, new)
    return text
