"""Add one bounded render-only phase; preserve native009's identity and hardware probes."""
import hashlib

def build_source(parent):
    assert hashlib.sha256(parent.encode()).hexdigest()=='6ea7bf8d7302c51d70f09dc1e6932c223698c5edb81a51edd858ec5010f5326d'
    anchor='                (void)probe("enumeration", enumerate, 10);'
    assert parent.count(anchor)==1
    return parent.replace(anchor,anchor+'''
                char *mesa[] = {"/bin/native-mesa-launcher-001", NULL};
                (void)probe("native-mesa-offscreen", mesa, 25);''')
