"""Replace only data provisioning and adaptation-owned per-boot diagnostics."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy
import subprocess
import sys
import uuid

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
BUILD=Path('/home/zoinve/harmony-virgl-883')
OLD_RUNTIME='81c2fb7d8a613b683c9ed6e4d278032f6dd7626af7995f263839bca791f9dda2'

def sha(data):return hashlib.sha256(data).hexdigest()

def runtime166(source):
    assert source.count('#define _GNU_SOURCE\n')==1
    source='#define _GNU_SOURCE\n'+source.replace('#define _GNU_SOURCE\n','',1)
    start=source.index('static void volatile_ext4_data_037(void)')
    end=source.index('\nstatic void guest_permissive_config_047',start)
    source=source[:start]+'''#include "persistent-runtime-166.h"
static void persistent_ext4_data166(void)
{
    int fd=open("/dev/loop3",O_RDWR|O_CLOEXEC), ro=1;
    if(fd<0 || ioctl(fd,BLKROGET,&ro) || ro) fail("persistent ext4 loop writable");
    close(fd);
    if(mount("/dev/loop3","/data","ext4",MS_NOSUID|MS_NODEV|MS_NOATIME,"data=ordered"))
        fail("persistent ext4 data mount");
    persistent_runtime166();
}
''' +source[end:]
    assert source.count('    volatile_ext4_data_037();')==1
    source=source.replace('    volatile_ext4_data_037();','    persistent_ext4_data166();',1)
    assert source.count('readonly_images=4 volatile_data=1')==1
    return source.replace('readonly_images=4 volatile_data=1','readonly_images=4 volatile_data=0 persistent_data=1',1)

def outer166(source,digest,filesystem_uuid):
    start=source.index('    if(okay){\n        char *seed123[]')
    end=source.index('\n    if(okay)native_live159_load();',start)
    assert 'ftruncate(ram,8589934592ULL)' in source[start:end]
    source=source[:start]+'    if(okay && persistent166_prepare())okay=0;\n'+source[end:]
    anchor='static void network081_kmsg(void)'
    assert source.count(anchor)==1
    values='{'+','.join(str(b) for b in uuid.UUID(filesystem_uuid).bytes)+'}'
    source=source.replace(anchor,'#define PERSISTENT166_UUID '+values+'\n#include "persistent-data-166.h"\n\n'+anchor,1)
    anchor='    for(unsigned i=0;i<5;++i)if(native_fds[i]>=0)close(native_fds[i]);'
    assert source.count(anchor)==1
    source=source.replace(anchor,'    persistent166_finish();\n'+anchor,1)
    old='/mnt/ubuntu/home/zoinve/.local/share/harmony-arm64-kvm-lab/commercial61-native-108/bootstrap-runtime087'
    assert source.count(old)==5 and source.count(OLD_RUNTIME)==2
    source=source.replace(old,old.replace('-108/','-166/')).replace(OLD_RUNTIME,digest)
    anchor='ram_data=%d\\n",i,ro,bytes,i==3'
    assert source.count(anchor)==1
    return source.replace(anchor,'ram_data=%d\\n",i,ro,bytes,0',1)

if __name__=='__main__':
    assert sys.argv[1:] in [[],['--compile-fix-1']]
    suffix='-compile-fix-1' if sys.argv[1:] else ''
    parent=BUILD/'commercial61-native-164'
    work=BUILD/('commercial61-native-166'+suffix)
    report=ROOT/('reports/commercial61-native-166'+suffix)
    assert not work.exists() and not report.exists(), 'preserve numbered builds'
    provision=json.loads((ROOT/'reports/persistent-data-165/provision.json').read_text())
    assert provision['offline_fsck_clean'] and provision['seed_unchanged']
    metadata=json.loads((ROOT/'reports/commercial61-native-164/result.json').read_text())
    for row in metadata['artifacts']:assert sha((parent/row['name']).read_bytes())==row['sha256']
    parser=runpy.run_path(str(BASE/'audit-commercial-network-inputs-079.py'))['members']
    member=runpy.run_path(str(BASE/'build-commercial-native-087.py'))['member']
    before={n:(m,b) for n,m,b in parser(gzip.decompress((parent/'initrd.img').read_bytes()))}
    previous=json.loads((ROOT/'reports/commercial61-native-164/overlay-result.json').read_text())
    assert sha((parent/'minimal-overlay.img').read_bytes())==previous['sha256']
    work.mkdir();report.mkdir()
    header=(BUILD/'commercial61-native-159/native-live-debug-159.h').read_bytes()
    expected=(BASE/'native-live-debug-157.h').read_text().replace('157','159').replace('live-debug-inputs-159','live-debug-inputs-157').encode()
    assert header==expected
    (work/'native-live-debug-159.h').open('xb').write(header)
    changed={'init','init.c','initrd.img','bootstrap-runtime087','bootstrap-runtime087.c'}
    for row in metadata['artifacts']:
        if row['name'] not in changed:(work/row['name']).open('xb').write((parent/row['name']).read_bytes())
    def compile_program(name,text,core=False):
        (work/(name+'.c')).open('x').write(text)
        args=['aarch64-linux-gnu-gcc','-static','-O2','-Wall','-Wextra','-Werror','-I',str(BASE),str(work/(name+'.c'))]
        if core:args.append(str(BASE/'baremetal-diagnostic-core.c'))
        p=subprocess.run(args+['-o',str(work/name)],capture_output=True,timeout=120)
        (report/(name+'.stderr')).open('xb').write(p.stderr)
        assert p.returncode==0,p.stderr.decode()
    compile_program('bootstrap-runtime087',runtime166((parent/'bootstrap-runtime087.c').read_text()))
    digest=sha((work/'bootstrap-runtime087').read_bytes())
    compile_program('init',outer166((parent/'init.c').read_text(),digest,provision['filesystem_uuid']),True)
    after=dict(before)
    after['init']=(before['init'][0],(work/'init').read_bytes())
    mode,wrapper=before['early-hardware093.sh']
    assert wrapper.count(sha(before['init'][1]).encode())==1
    after['early-hardware093.sh']=(mode,wrapper.replace(sha(before['init'][1]).encode(),sha(after['init'][1]).encode(),1))
    delta={n:v for n,v in after.items() if before.get(n)!=v}
    assert set(delta)=={'init','early-hardware093.sh'}
    def archive(entries):
        raw=b''.join(member(n,m,b,i+1) for i,(n,(m,b)) in enumerate(entries.items()))
        return gzip.compress(raw+member('TRAILER!!!',0,b'',len(entries)+1),compresslevel=6,mtime=0)
    (work/'initrd.img').open('xb').write(archive(after))
    minimal={n:(m,b) for n,m,b in parser(gzip.decompress((parent/'minimal-overlay.img').read_bytes()))}
    minimal.update(delta)
    overlay=archive(minimal)
    (work/'minimal-overlay.img').open('xb').write(overlay)
    chain=previous['chain'][:-1]+['commercial61-native-166/initrd.img']
    metadata['artifacts']=[dict(name=row['name'],bytes=(work/row['name']).stat().st_size,
        sha256=sha((work/row['name']).read_bytes())) for row in metadata['artifacts']]
    metadata['runtime_verified']=False
    metadata['volatile_data_capacity_bytes']=0
    metadata['persistent166']=dict(capacity_bytes=8589934592,data_path=provision['data_path'],
        filesystem_uuid=provision['filesystem_uuid'],runtime_bootstrap_sha256=digest,
        original_runtime_sha256=OLD_RUNTIME,seed_reset_on_boot=False,original_images_modified=False,
        persistent_header_sha256=sha((BASE/'persistent-data-166.h').read_bytes()),
        runtime_header_sha256=sha((BASE/'persistent-runtime-166.h').read_bytes()),
        live_debug164_unchanged=True,cross_boot_persistence_verified=False)
    overlay_result=dict(bytes=len(overlay),sha256=sha(overlay),members=sorted(minimal),chain=chain,
        changed_from_full_parent=sorted(delta),shared_parent_overlay_sha256=previous['shared_parent_overlay_sha256'],
        ordered_chain_equals_full_166=True,existing_016_overlay_sha256=previous['existing_016_overlay_sha256'],
        original_images_written=False,runtime_verified=False)
    for folder in [work,report]:
        (folder/'result.json').open('x').write(json.dumps(metadata,indent=2))
        (folder/'overlay-result.json').open('x').write(json.dumps(overlay_result,indent=2))
    print(json.dumps(dict(persistent166=metadata['persistent166'],overlay=overlay_result),indent=2))
