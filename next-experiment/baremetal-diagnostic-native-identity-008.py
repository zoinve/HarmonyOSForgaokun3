"""Add only a bounded, non-mutating identity read to the known 007 diagnostic."""
import hashlib

def build_source(parent):
    assert hashlib.sha256(parent.encode()).hexdigest()=='17cd7bc58ef63abd35ab66265eeaf6deef12193660d7cf8f35e8ac0235649436'
    anchor='            char *bindings[]'
    assert parent.count(anchor)==1
    return parent.replace(anchor,'''            char *identity_read[] = {"/bin/native-identity-read-001", NULL};
            (void)probe("native-identity-read", identity_read, 8);
'''+anchor)
