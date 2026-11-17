"""Admit only the independently audited existing Ubuntu diagnostic session."""
def validate(state):
    assert state['os_id']=='ubuntu'
    assert state['boot_id']=='f6df309e-a8c1-4f00-8ec6-fc6e421f0e85'
    assert state['release']=='7.1.0-rc3-gaokun3-ego-s4diag1'
    assert state['root_uuid']=='ecdd7931-ca18-4d14-82cd-ba3c62ff7365'
    assert state['entry_sha256']=='0c505e8371daa2615ad47e9bda4f575cdaa634e122b60b5f6d7cfe91dd52ebfd'
    lines={line.strip() for line in state['status'].splitlines()}
    assert 'Default Entry: 8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf' in lines
    assert 'Current Entry: ego-s4diag-20261113.conf' in lines
    assert 'OneShot Entry:' not in state['status']
