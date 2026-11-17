"""Give only SceneBoard the canonical name for its already-visible config tree."""
import copy


def repair(original):
    groups = [common for common in original['common'] if common.get('app-base')]
    assert len(groups) == 1 and groups[0]['top-sandbox-switch'] == 'ON'
    bases = groups[0]['app-base']
    assert len(bases) == 1
    mounts = bases[0]['mount-paths']
    config = [m for m in mounts if m.get('src-path') == '/system/etc' and m.get('sandbox-path') == '/system/etc']
    assert len(config) == 1 and config[0]['sandbox-flags'] == ['bind', 'rec']
    assert any(m.get('src-path') == '/system/lib64' and m.get('sandbox-path') == '/usr/system/lib64' for m in mounts)
    individuals = [group['com.ohos.sceneboard'] for group in original['individual'] if 'com.ohos.sceneboard' in group]
    assert len(individuals) == 1 and len(individuals[0]) == 1
    scene = individuals[0][0]
    assert scene['sandbox-switch'] == 'ON'
    assert not any(m.get('sandbox-path', '').startswith('/usr/system/etc') for m in scene['mount-paths'])
    assert not any(link.get('link-name') in ('/usr', '/usr/system', '/usr/system/etc') for link in scene['symbol-links'])
    result = copy.deepcopy(original)
    target = next(group['com.ohos.sceneboard'][0] for group in result['individual'] if 'com.ohos.sceneboard' in group)
    alias = copy.deepcopy(config[0])
    alias.update({'sandbox-path': '/usr/system/etc', 'check-action-status': 'true'})
    target['mount-paths'].append(alias)
    return result
