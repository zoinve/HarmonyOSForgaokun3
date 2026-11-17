"""Offline own-source Mesa rebuild against ISO C++ ABI; never accesses the device."""
from pathlib import Path
import runpy,subprocess

base=Path(__file__).resolve().parent
payload=runpy.run_path(str(base/'build-baremetal-mesa-freedreno-003.py'))['build_payload']()
for old,new in [('baremetal-mesa-freedreno-003','commercial-mesa-011'),
                ('baremetal-mesa-freedreno-build-003','commercial-mesa-011'),
                ('lab-freedreno003','lab-commercial011')]:
    assert old in payload
    payload=payload.replace(old,new)
start=payload.index("original=(root/'toolchain/ohos-cross.ini').read_text()")
end=payload.index("(report/'source-before.json')",start)
toolchain=r'''
runtime=work/'runtime';runtime.mkdir()
commercial=root/'commercial-graphics-link-009/runtime'
for name in ['libc.so','libc++.so']:
 shutil.copyfile(commercial/name,runtime/name)
headers=root/'sdk/native'
common=['--target=aarch64-linux-ohos','--sysroot='+str(headers/'sysroot'),
 '-resource-dir='+str(headers/'llvm/lib/clang/15.0.4')]
for name,cxx in [('cc',False),('cxx',True)]:
 fixed=['clang++-19' if cxx else 'clang-19',*common]
 if cxx:fixed+=['-stdlib=libc++','-nostdlib++','-nostdinc++',
  '-isystem',str(root/'window-bridge/toolchain/platform-cxx-headers'),
  '-isystem',str(headers/'llvm/include/libcxx-ohos/include/c++/v1')]
 linking=['-fuse-ld=lld','-rtlib=compiler-rt','-L'+str(runtime),
  '-L'+str(headers/'llvm/lib/aarch64-linux-ohos'),'-Wl,-z,max-page-size=65536']
 tail=[str(runtime/'libc++.so'),str(runtime/'libc.so')] if cxx else [str(runtime/'libc.so')]
 script='#!/usr/bin/python3\nimport os,sys\na=sys.argv[1:]\n'
 script+='compile_only=any(x in a for x in ["-c","-E","-S","-fsyntax-only","--print-search-dirs","-dumpmachine"])\n'
 script+='cmd='+repr(fixed)+'+([] if compile_only else '+repr(linking)+')+a+([] if compile_only else '+repr(tail)+')\n'
 script+='os.execvp(cmd[0],cmd)\n'
 p=work/name;p.write_text(script);p.chmod(0o700)
original=(root/'toolchain/ohos-cross.ini').read_text()
original=original.replace(str(root/'toolchain/ohos-cc'),str(work/'cc')).replace(str(root/'toolchain/ohos-cxx'),str(work/'cxx'))
original=original.replace('-Wl,-rpath,/system/lib64/lab-virgl883','-Wl,-rpath,/system/lib64/lab-commercial011')
cross.write_text(original)
'''
payload=payload[:start]+toolchain+'\n'+payload[end:]
anchor="    result['build_success']=True"
assert payload.count(anchor)==1
payload=payload.replace(anchor,"""    result['sdk_runtime_libraries_used']=False
    result['original_commercial_runtime_linked']=True
    result['commercial_runtime_sha256']={n:sha(runtime/n) for n in ['libc.so','libc++.so']}
    result['commercial_runtime_source_unchanged']=all(sha(runtime/n)==sha(commercial/n) for n in ['libc.so','libc++.so'])
    result['target_rendering_verified']=False
    result['deployed']=False
"""+anchor)
if __name__=='__main__':
    report=base.parent/'reports/commercial-mesa-011'
    assert not report.exists(),'preserve numbered builds'
    report.mkdir()
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=3100).returncode)
