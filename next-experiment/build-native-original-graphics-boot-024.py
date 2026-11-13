"""One performance variable: bulk DMA transfer around cacheable RAM rotation."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-native-original-graphics-boot-023.py'))
inner=p['inner'];outer=p['outer'].replace('native-original-023-%s','native-original-024-%s')
payload=p['payload'].replace('native-original-graphics-boot-023','native-original-graphics-boot-024')
# Replace only the outer generated literal, not the completed 023 candidate.
assert 'outer='+repr(p['outer']) in payload
payload=payload.replace('outer='+repr(p['outer']),'outer='+repr(outer),1)
adaptation=r'''
cached_header=project/'next-experiment/native-cached-copy-024.h'
(work/cached_header.name).write_bytes(cached_header.read_bytes())
source=source.replace('#include "native-landscape-copy-023.h"','#include "native-cached-copy-024.h"')
old='    landscape_copy_023(static_cast<unsigned char *>(output.map),output.pitch,'
assert source.count(old)==1
source=source.replace(old,'    static std::vector<unsigned char> cache_in_024,cache_out_024;\n    cached_landscape_copy_024(static_cast<unsigned char *>(output.map),output.pitch,')
old='        client.stride,crop.x,crop.y,crop.w,crop.h,rgba);'
assert source.count(old)==1
source=source.replace(old,'        client.stride,crop.x,crop.y,crop.w,crop.h,rgba,cache_in_024,cache_out_024);')
with (local/'cached-copy.json').open('x') as f:
 json.dump(dict(cached_copy_source_sha256=sha(cached_header),dma_ownership_unchanged=True,egl_readback_unchanged=True,input_and_identities_unchanged=True),f,indent=2)
'''
anchor="src=work/'composer-trace.cpp';src.write_text(source)"
assert payload.count(anchor)==1
payload=payload.replace(anchor,adaptation+'\n'+anchor)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
