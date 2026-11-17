"""Use existing commercial resources instead of missing Kirin development trees."""
import copy

def repair(original):
    groups=[g['com.ohos.sceneboard'] for g in original['individual'] if 'com.ohos.sceneboard' in g]
    assert len(groups)==1 and len(groups[0])==1
    block=groups[0][0]
    assert block['sandbox-switch']=='ON'
    assert any(m.get('src-path')=='/system/lib64' and m.get('sandbox-path')=='/system/lib64'
               for g in original['common'] for b in g.get('app-base',[]) for m in b['mount-paths'])
    changes={
        '/vendor/lib64/passthrough':('/data/local/tmp/l410-sceneboard-r18-passthrough-v2','/system/lib64'),
        '/system/app/SceneBoard':('/data/local/tmp/l410-fp-completion-v3/SceneBoard','/system/app/SceneBoard')}
    new=copy.deepcopy(original)
    target=[g['com.ohos.sceneboard'][0] for g in new['individual'] if 'com.ohos.sceneboard' in g][0]
    for destination,(source,replacement) in changes.items():
        matches=[m for m in target['mount-paths'] if m.get('sandbox-path')==destination]
        assert len(matches)==1
        mount=matches[0]
        assert mount['src-path']==source
        assert mount['sandbox-flags']==['bind','rec'] and mount['check-action-status']=='true'
        mount['src-path']=replacement
    return new
