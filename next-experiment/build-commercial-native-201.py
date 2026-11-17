'''Retain desktop runtime; add a fixed Settings launch and teardown reason codes.'''
from pathlib import Path
import gzip
import hashlib
import json
import runpy
import subprocess

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
BUILD=Path('/home/zoinve/harmony-virgl-883')
ADAPT=runpy.run_path(str(BASE/'settings-native-201.py'))


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    parent=BUILD/'commercial61-native-197-r1'
    work=BUILD/'commercial61-native-201';report=ROOT/'reports/commercial61-native-201'
    assert not work.exists() and not report.exists(),'preserve numbered builds'
    offline=json.loads((ROOT/'reports/commercial61-native-197-r1/settings-data-offline-199.json').read_text())
    state=json.loads((ROOT/'reports/settings-live-state-200/target.json').read_text())
    assert offline['filesystem_clean'] and offline['active165_unchanged_from_predeployment']
    assert offline['lab_partition_unmounted'] and state['lab_partition_unmounted']
    assert all(state['unique_settings_user100_token_match'].values())
    assert offline['candidate_sha256_after_boot']=='41fae8e1ceacedd356da6e6d712aa8a995179c042221657f4d8e2deace9938c6'
    metadata=json.loads((parent/'result.json').read_text())
    previous=json.loads((parent/'overlay-result.json').read_text())
    for row in metadata['artifacts']:assert sha((parent/row['name']).read_bytes())==row['sha256']
    assert sha((parent/'bootstrap-runtime087').read_bytes())=='fe80eef0831fda293ff0bbebb66f9c2d0c6c8c6b739b47cc8714653479ea7122'
    parser=runpy.run_path(str(BASE/'audit-commercial-network-inputs-079.py'))['members']
    member=runpy.run_path(str(BASE/'build-commercial-native-087.py'))['member']
    before={n:(m,b) for n,m,b in parser(gzip.decompress((parent/'initrd.img').read_bytes()))}
    work.mkdir();report.mkdir()
    for row in metadata['artifacts']:
        if row['name'] not in {'init','init.c','initrd.img'}:
            (work/row['name']).open('xb').write((parent/row['name']).read_bytes())
    headers={
        'persistent-data-166.h':(parent/'persistent-data-166.h').read_bytes(),
        'persistent-data-172.h':ADAPT['lifecycle201']((BASE/'persistent-data-172.h').read_text()).encode(),
        'persistent-unmount-plan-201.h':ADAPT['plan201']((BASE/'persistent-unmount-plan-172.h').read_text()).encode(),
        'settings-launch-201.h':(BASE/'settings-launch-201.h').read_bytes(),
        'native-live-debug-159.h':(parent/'native-live-debug-159.h').read_bytes(),
    }
    for name,data in headers.items():(work/name).open('xb').write(data)
    (work/'init.c').open('x').write(ADAPT['outer201']((parent/'init.c').read_text()))
    args=['aarch64-linux-gnu-gcc','-static','-O2','-Wall','-Wextra','-Werror','-I',str(BASE),
          str(work/'init.c'),str(BASE/'baremetal-diagnostic-core.c'),'-o',str(work/'init')]
    proc=subprocess.run(args,capture_output=True,timeout=120)
    (report/'init.stderr').open('xb').write(proc.stderr)
    assert proc.returncode==0,proc.stderr.decode()
    after=dict(before);after['init']=(before['init'][0],(work/'init').read_bytes())
    mode,wrapper=before['early-hardware093.sh']
    assert wrapper.count(sha(before['init'][1]).encode())==1
    after['early-hardware093.sh']=(mode,wrapper.replace(sha(before['init'][1]).encode(),sha(after['init'][1]).encode(),1))
    delta={name:row for name,row in after.items() if before.get(name)!=row}
    assert set(delta)=={'init','early-hardware093.sh'}
    def archive(entries):
        raw=b''.join(member(n,m,b,i+1) for i,(n,(m,b)) in enumerate(entries.items()))
        return gzip.compress(raw+member('TRAILER!!!',0,b'',len(entries)+1),compresslevel=6,mtime=0)
    (work/'initrd.img').open('xb').write(archive(after))
    minimal={n:(m,b) for n,m,b in parser(gzip.decompress((parent/'minimal-overlay.img').read_bytes()))}
    minimal.update(delta);overlay=archive(minimal)
    (work/'minimal-overlay.img').open('xb').write(overlay)
    replay=dict(before);replay.update({n:(m,b) for n,m,b in parser(gzip.decompress(overlay))})
    assert replay==after
    for name in ['bootstrap-runtime087','bootstrap-runtime087.c']:
        assert (work/name).read_bytes()==(parent/name).read_bytes()
    metadata['artifacts']=[dict(name=row['name'],bytes=(work/row['name']).stat().st_size,
        sha256=sha((work/row['name']).read_bytes())) for row in metadata['artifacts']]
    metadata.pop('settings197')
    metadata['persistent166']['persistent_header_sha256']=sha(headers['persistent-data-172.h'])
    metadata['runtime_verified']=False
    metadata['settings201']=dict(expected_preboot_candidate_sha256=offline['candidate_sha256_after_boot'],
        desktop173_runtime_and_source_byte_identical=True,application_launch_requests=1,
        original_aa_ams_and_security_checks=True,original_service_created_state_retained=True,
        active_data165_modified=False,usb_work_paused=True,installed_or_booted=False,
        settings_window_verified=False,teardown_failure123_not_yet_resolved=True,
        header_hashes={name:sha(data) for name,data in headers.items()})
    overlay_result=dict(previous,bytes=len(overlay),sha256=sha(overlay),
        chain=previous['chain'][:-1]+['commercial61-native-201/initrd.img'],
        ordered_chain_equals_full_201=True,parent_full_sha256=sha((parent/'initrd.img').read_bytes()),
        chain_verification_basis='pinned_full197_plus201_overlay_pending_independent_admission')
    overlay_result.pop('ordered_chain_equals_full_197')
    for folder in [work,report]:
        (folder/'result.json').open('x').write(json.dumps(metadata,indent=2))
        (folder/'overlay-result.json').open('x').write(json.dumps(overlay_result,indent=2))
    print(json.dumps(metadata['settings201'],indent=2))


if __name__=='__main__':main()
