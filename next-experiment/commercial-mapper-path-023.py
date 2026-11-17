"""Keep original mapper services visible in the already-granted vendor tree."""
import copy
def repair(original):
    assert any(m.get('src-path')=='/vendor/lib64' and m.get('sandbox-path')=='/vendor/lib64'
               for g in original['common'] for b in g.get('app-base',[]) for m in b['mount-paths'])
    new=copy.deepcopy(original)
    groups=[g['com.ohos.sceneboard'] for g in new['individual'] if 'com.ohos.sceneboard' in g]
    assert len(groups)==1 and len(groups[0])==1
    block=groups[0][0];assert block['sandbox-switch']=='ON'
    mounts=[m for m in block['mount-paths'] if m.get('sandbox-path')=='/vendor/lib64/passthrough']
    assert len(mounts)==1
    mount=mounts[0]
    assert mount['src-path']=='/system/lib64'
    assert mount['sandbox-flags']==['bind','rec'] and mount['check-action-status']=='true'
    mount['src-path']='/vendor/lib64/passthrough'
    return new
