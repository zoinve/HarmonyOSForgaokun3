"""Install real backlight entrypoints with a narrow original-composer sysfs rule."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy
import subprocess

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
BUILD=Path('/home/zoinve/harmony-virgl-883')
def sha(data):return hashlib.sha256(data).hexdigest()

def adapt(source):
    anchor='#include "commercial-safety-010.h"'
    assert source.count(anchor)==1
    source=source.replace(anchor,anchor+'\n#include "native-backlight-permissions-130.h"',1)
    anchor='    if(okay){\n        /* Only the temporary diagnostic kernel:'
    assert source.count(anchor)==1
    addition='''    if(okay && native_backlight_permissions130()){
        dprintf(1,"GAOKUN_BACKLIGHT130_REFUSED errno=%d\\n",errno);okay=0;
    }
'''
    return source.replace(anchor,addition+anchor,1)

if __name__=='__main__':
    work=BUILD/'commercial61-native-130';report=ROOT/'reports/commercial61-native-130'
    assert not work.exists() and not report.exists()
    parent=BUILD/'commercial61-native-123'
    previous=json.loads((ROOT/'reports/commercial61-native-123/result.json').read_text())
    for item in previous['artifacts']:
        assert sha((parent/item['name']).read_bytes())==item['sha256']
    parse=runpy.run_path(str(BASE/'audit-commercial-network-inputs-079.py'))['members']
    pack=runpy.run_path(str(BASE/'build-commercial-native-087.py'))['member']
    before={name:(mode,data) for name,mode,data in parse(gzip.decompress((parent/'initrd.img').read_bytes()))}
    after=dict(before)
    composer=json.loads((ROOT/'reports/commercial-composer-129/result.json').read_text())
    library=(BUILD/'commercial-composer-129/libdisplay_composer_vdi_impl.z.so').read_bytes()
    assert sha(library)==composer['composer_sha256']
    candidates=[name for name in before if name.endswith('/libdisplay_composer_vdi_impl.z.so') and '/graphics016/' in '/'+name]
    assert len(candidates)==1,candidates
    library_name=candidates[0]
    assert sha(before[library_name][1])==composer['parent_composer_sha256']
    work.mkdir();report.mkdir()
    for item in previous['artifacts']:
        if item['name'] not in ['init','init.c','initrd.img']:
            (work/item['name']).open('xb').write((parent/item['name']).read_bytes())
    outer=adapt((parent/'init.c').read_text())
    (work/'init.c').open('x').write(outer)
    compiled=subprocess.run(['aarch64-linux-gnu-gcc','-static','-O2','-Wall','-Wextra','-Werror',str(work/'init.c'),'-I',str(BASE),str(BASE/'baremetal-diagnostic-core.c'),'-o',str(work/'init')],capture_output=True)
    (report/'init.stderr').open('xb').write(compiled.stderr)
    assert compiled.returncode==0,compiled.stderr.decode(errors='replace')
    after['init']=(before['init'][0],(work/'init').read_bytes())
    mode,wrapper=before['early-hardware093.sh']
    assert wrapper.count(sha(before['init'][1]).encode())==1
    after['early-hardware093.sh']=(mode,wrapper.replace(sha(before['init'][1]).encode(),sha(after['init'][1]).encode(),1))
    after[library_name]=(before[library_name][0],library)
    delta={name:value for name,value in after.items() if before.get(name)!=value}
    assert set(delta)=={'init','early-hardware093.sh',library_name}
    def archive(entries):
        raw=b''.join(pack(name,mode,data,index+1) for index,(name,(mode,data)) in enumerate(entries.items()))
        return gzip.compress(raw+pack('TRAILER!!!',0,b'',len(entries)+1),compresslevel=6,mtime=0)
    (work/'initrd.img').open('xb').write(archive(after))
    overlay=archive(delta)
    (work/'minimal-overlay.img').open('xb').write(overlay)
    chain=json.loads((ROOT/'reports/commercial61-native-124/admission-test.json').read_text())['chain']
    assert chain[-1]=='commercial61-native-123/initrd.img'
    # 123 contains only init/wrapper, both completely superseded by 130.
    assert json.loads((ROOT/'reports/commercial61-native-123/overlay-result.json').read_text())['members']==['early-hardware093.sh','init']
    chain=chain[:-1]+['commercial61-native-130/initrd.img']
    parent_overlay=json.loads((ROOT/'reports/commercial61-native-123/overlay-result.json').read_text())
    overlay_result=dict(bytes=len(overlay),sha256=sha(overlay),members=sorted(delta),chain=chain,
        shared_parent_overlay_sha256=parent_overlay['sha256'],ordered_chain_equals_full_130=True,
        existing_016_overlay_sha256=parent_overlay['existing_016_overlay_sha256'],original_images_written=False,runtime_verified=False)
    previous['artifacts']=[dict(name=row['name'],bytes=(work/row['name']).stat().st_size,sha256=sha((work/row['name']).read_bytes())) for row in previous['artifacts']]
    previous['driver130']=dict(composer_sha256=sha(library),library_archive_path=library_name,native_hdi_maximum=65535,
        composer_primary_credentials_unchanged=True,sysfs_writer_group=3036,sysfs_brightness_mode='0660',
        original_runtime_and_seed_unchanged=True,no_oobe_experiment=True,target_runtime_verified=False)
    previous['runtime_verified']=False
    for directory in [work,report]:
        (directory/'result.json').open('x').write(json.dumps(previous,indent=2))
        (directory/'overlay-result.json').open('x').write(json.dumps(overlay_result,indent=2))
    print(json.dumps(previous['driver130'],indent=2))
