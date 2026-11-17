"""Alias the existing commercial /system view; grant no additional mounts."""
import copy

def repair(original):
    assert original['sandbox-root'] in ('/mnt/sandbox/system', '/mnt/sandbox/chipset')
    assert any(item.get('src-path') == '/system/profile' and item.get('sandbox-path') == '/system/profile'
               for item in original['mount-bind-paths']), 'profile must already be exposed'
    assert all(item['link-name'] not in ('/usr', '/usr/system')
               for item in original.get('symbol-links', [])), 'conflicting or repeated alias'
    new = copy.deepcopy(original)
    new.setdefault('symbol-links', []).append({'target-name': '/system', 'link-name': '/usr/system'})
    return new
