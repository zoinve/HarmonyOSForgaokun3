"""Only replace the binderfs-only helper with the independently tested legacy read helper."""
import hashlib

def build_source(parent):
    assert hashlib.sha256(parent.encode()).hexdigest()=='870c4511f77b54752a2cacdca5e8fb8f465c6615bdb84acbdd4c8c1317c96ffc'
    assert parent.count('/bin/native-identity-read-001')==1
    return parent.replace('/bin/native-identity-read-001','/bin/native-identity-read-002')
