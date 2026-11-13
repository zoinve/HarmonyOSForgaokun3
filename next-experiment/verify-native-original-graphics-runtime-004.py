"""Read-only 004 evidence verification, without equating launch to readiness."""
from pathlib import Path
import runpy,re,json
base=Path(__file__).resolve().parent
previous=runpy.run_path(str(base/'verify-native-original-graphics-runtime-003.py'))['verify']
def verify(root, data_bytes=536870912):
    result=previous(root, data_bytes=data_bytes)
    d=json.loads((root/'runtime-result.json').read_text())
    text=(root/'native-logs'/d['logs'][-1]['name']).read_bytes().decode(errors='replace')
    rows=re.findall(r'NATIVE_DAC004 path=(\S+) rc=(-?\d+) mode=(\d+) uid=(\d+) gid=(\d+)',text)
    assert rows, 'DAC diagnostics missing'
    for path in ['/system','/vendor','/run/system-upper','/run/vendor-upper']:
        assert any(p==path and rc=='0' and mode=='40755' for p,rc,mode,uid,gid in rows),path
    services={}
    for name,uid in [('render_service',1003),('foundation',5523),('composer_host',3036),('allocator_host',3041)]:
        observed=re.findall(r'NATIVE_GRAPHICS001_PROCESS sample=(\d+) pid=(\d+) cmd=([^\n]+)',text)
        hits=[(sample,pid) for sample,pid,cmd in observed if name in cmd]
        assert hits,name+' not observed'
        pids=sorted(set(pid for sample,pid in hits))
        for pid in pids:
            assert re.search(r'NATIVE_GRAPHICS001_IDENTITY pid='+pid+r' Uid:\s*'+str(uid)+r'\s+'+str(uid)+r'\s+'+str(uid)+r'\s+'+str(uid)+r'\s*\n',text)
            assert f'NATIVE_GRAPHICS001_DOMAIN pid={pid} value=u:r:{name}:s0' in text
        services[name]=dict(pids=pids,samples=sorted(set(int(sample) for sample,pid in hits)),uid=uid,domain='u:r:'+name+':s0')
    rs=services['render_service']['pids']
    assert any(re.search(r'NATIVE_GRAPHICS001_MAP pid='+pid+r' [^\n]*/lab-freedreno003/libgallium-25.0.1.so',text) for pid in rs)
    result.update(overlay_root_modes_verified=True,dac_states=rows,original_service_identities=services,
        exec_permission_failure_lines=[l for l in text.splitlines() if re.search(r'failed to execv \d+ 13 ',l)],
        observed_processes=sorted(set(re.findall(r'NATIVE_GRAPHICS001_PROCESS sample=\d+ pid=\d+ cmd=([^\n]+)',text))),
        native_mesa_map_samples=len(re.findall(r'NATIVE_GRAPHICS001_MAP [^\n]*lab-freedreno003',text)),
        desktop_verified=False)
    return result
if __name__=='__main__':
    print(json.dumps(verify(base.parent/'reports/native-original-graphics-boot-004'),indent=2))
