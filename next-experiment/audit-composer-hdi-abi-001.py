"""Offline original-SDK ABI characterization; no ELF execution or device access."""
from pathlib import Path
import hashlib
import json
import subprocess

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / 'reports/composer-hdi-abi-001'

PAYLOAD = r'''
from pathlib import Path
import hashlib,json,subprocess
r=Path('/home/zoinve/harmony-virgl-883')
b=r/'composer-service-957-build2'
ref=Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports/graphics')
service=b/'libdisplay_composer_service_1.5.z.so'
manifest=json.loads(Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment/official-composer-service-957/manifest.json').read_text())
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dependencies=[]
for row in manifest['added_original_dependencies']:
 p=b/row['name'];h=digest(p)
 assert h==row['sha256'],str(p)
 dependencies.append(dict(path=str(p),sha256=h,bytes=p.stat().st_size))
assert digest(service)=='c5f7b2430aac4bee8edbeaea707805c0d9f33f6ee762a4a1f82452be01f92aab'
assert digest(ref/'composer.cpp')=='9d2536a61c40aef948f48c482a081cdc2794d832d0775cee6bd9de87bdfa1b5a'
witness='#include "'+str(ref/'include/composer_abi.h')+'"\n#include <type_traits>\nstatic_assert(std::is_same<std::string,std::__h::basic_string<char>>::value,"platform namespace");\n'
flags=['-std=c++17','-Werror','-Wno-unused-command-line-argument','-x','c++','-fsyntax-only','-']
commands={
 'public-sdk-negative':['clang++-19','--target=aarch64-linux-ohos','--sysroot='+str(r/'sdk/native/sysroot'),'-resource-dir='+str(r/'sdk/native/llvm/lib/clang/15.0.4'),'-nostdinc++','-isystem',str(r/'sdk/native/llvm/include/libcxx-ohos/include/c++/v1')]+flags,
 'platform-positive':[str(r/'window-bridge/toolchain/ohos-platform-cxx')]+flags,
 'service-symbols':['aarch64-linux-gnu-nm','-DC',str(service)],
 'service-dynamic':['aarch64-linux-gnu-readelf','-dW',str(service)],
 'service-loader-disassembly':['aarch64-linux-gnu-objdump','-dC','--start-address=0xf138','--stop-address=0xfc4c',str(service)],
}
results={}
for name,command in commands.items():
 p=subprocess.run(command,input=witness if name.endswith(('negative','positive')) else None,text=True,capture_output=True,timeout=30)
 results[name]=dict(command=command,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)
n=results['public-sdk-negative'];p=results['platform-positive']
assert n['returncode']!=0 and "no member named '__h'" in n['stderr'],n
assert p['returncode']==0 and not p['stderr'],p
for name in ('service-symbols','service-dynamic','service-loader-disassembly'):
 assert results[name]['returncode']==0,results[name]
symbols=results['service-symbols']['stdout']
prefix='OHOS::HDI::Display::Composer::DisplayComposerService::'
for name in ('InitCmdRequest(', 'CmdRequest(', 'DoCmdRequest(', 'InitSMQInfo(', 'GetCmdReply(', 'ClearClientBuffer(', 'GetDisplayCapability(', 'GetDisplaySupportedModes('):
 assert prefix+name in symbols,name
assert prefix+'SetDisplayClientBuffer(' not in symbols
assert 'DeviceCache::SetDisplayClientBuffer(' in symbols
assert 'std::__h::' in symbols and 'std::__n1::' not in symbols
inputs=[service,ref/'composer.cpp',ref/'include/composer_abi.h',r/'window-bridge/toolchain/ohos-platform-cxx',r/'window-bridge/toolchain/platform-cxx-headers/__config_site',r/'window-bridge/platform-root/system/lib64/libc++.so']
print(json.dumps(dict(inputs=[dict(path=str(p),sha256=digest(p),bytes=p.stat().st_size) for p in inputs],dependencies=dependencies,witness=witness,results=results)))
'''


def main():
    assert not OUT.exists(), OUT
    p = subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                       input=PAYLOAD, text=True, capture_output=True, timeout=180)
    assert p.returncode == 0, p.stderr
    data = json.loads(p.stdout)
    OUT.mkdir()
    artifacts = []
    for name, result in data['results'].items():
        for stream in ('stdout', 'stderr'):
            path = OUT / (name + '.' + stream)
            body = result[stream].encode()
            with path.open('xb') as f:
                f.write(body)
            artifacts.append(dict(path=path.name, bytes=len(body),
                                  sha256=hashlib.sha256(body).hexdigest()))
    with (OUT / 'witness.cpp').open('xb') as f:
        f.write(data['witness'].encode())
    result = dict(
        inputs=data['inputs'], original_dependencies=data['dependencies'],
        commands={name: dict(command=row['command'], returncode=row['returncode'])
                  for name, row in data['results'].items()}, artifacts=artifacts,
        public_sdk_namespace_refused=True, platform_namespace_and_layout_compile_pass=True,
        service_uses_smq_command_and_fd_cache_contract=True,
        direct_client_buffer_service_export_present=False,
        elf_executed=False, device_access=False, remote_changes=False,
        native_hdi_runtime_verified=False, serialization_verified=False,
        renderservice_verified=False, desktop_verified=False)
    with (OUT / 'result.json').open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
