"""Original fixtures plus tokenless association, fd/handle isolation and immutability."""
from pathlib import Path
import runpy
import subprocess
import tempfile

base = Path(__file__).resolve().parent
source = (base / 'test-commercial-binder-observer-043.cpp').read_text().replace('043', '044')
anchor = '    return 0;'
assert source.count(anchor) == 1
source = source.replace(anchor, r'''
    command=BC_TRANSACTION;
    stream.resize(4+sizeof(transaction));
    transaction.code=32;
    memcpy(stream.data(),&command,4);
    memcpy(stream.data()+4,&transaction,sizeof(transaction));
    request.write_buffer=reinterpret_cast<uintptr_t>(stream.data());
    request.write_size=stream.size();
    assert(snapshots044(request,snapshot,2,7)==1);
    assert(snapshot[0].interface==1);
    std::vector<unsigned char> bare(128,0);
    transaction.code=0;
    transaction.data_size=bare.size();
    transaction.data.ptr.buffer=reinterpret_cast<uintptr_t>(bare.data());
    memcpy(stream.data()+4,&transaction,sizeof(transaction));
    original=stream;
    assert(snapshots044(request,snapshot,2,7)==1);
    assert(snapshot[0].interface==3 && snapshot[0].code==0);
    assert(!snapshots044(request,snapshot,2,8));
    transaction.target.handle=43;
    memcpy(stream.data()+4,&transaction,sizeof(transaction));
    assert(!snapshots044(request,snapshot,2,7));
    transaction.target.handle=42;
    transaction.code=17;
    memcpy(stream.data()+4,&transaction,sizeof(transaction));
    auto before=stream;
    assert(snapshots044(request,snapshot,2,7)==1);
    assert(snapshot[0].interface==3 && snapshot[0].code==17);
    assert(stream==before);
    transaction.code=18;
    memcpy(stream.data()+4,&transaction,sizeof(transaction));
    assert(!snapshots044(request,snapshot,2,7));
    assert(!connection_handle044(65536,42,true));
    assert(!connection_handle044(7,0x1000000,true));
    assert(parcel==untouched);
''' + anchor, 1)
with tempfile.TemporaryDirectory(prefix='commercial-binder044-') as directory:
    root = Path(directory)
    (root / 'commercial-binder-observer-044.h').write_text(runpy.run_path(str(base / 'commercial-binder-observer-044.py'))['source']())
    (root / 'test.cpp').write_text(source)
    binary = root / 'test'
    subprocess.run(['g++', '-std=c++17', '-O2', '-Wall', '-Wextra', '-Werror',
                    '-fsanitize=address,undefined', str(root / 'test.cpp'), '-o', str(binary)], check=True, timeout=60)
    subprocess.run([str(binary)], check=True, timeout=20)
print('PASS: original Binder fixtures plus tokenless learned association and fd/handle isolation; no request mutation')
