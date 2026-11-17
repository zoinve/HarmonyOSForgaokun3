"""Expose an existing library mount under its original configuration-layer name."""
import copy

def repair(original):
    groups=[common for common in original['common'] if common.get('app-base')]
    assert len(groups)==1 and groups[0]['top-sandbox-switch']=='ON'
    bases=groups[0]['app-base']
    assert len(bases)==1
    current=bases[0]
    assert '<PackageName>' in current['sandbox-root']
    mounts=current['mount-paths']
    existing=[m for m in mounts if m.get('src-path')=='/system/lib64'
              and m.get('sandbox-path')=='/system/lib64']
    assert len(existing)==1, 'library tree must already be exposed'
    assert existing[0]['sandbox-flags']==['bind','rec']
    assert not any(m.get('sandbox-path','').startswith('/usr') for m in mounts)
    assert not any(l.get('link-name','').startswith('/usr') for l in current.get('symbol-links', []))
    alias=copy.deepcopy(existing[0])
    alias['sandbox-path']='/usr/system/lib64'
    alias['check-action-status']='true'
    new=copy.deepcopy(original)
    target=[b for common in new['common'] for b in common.get('app-base', [])][0]
    target['mount-paths'].append(alias)
    return new
