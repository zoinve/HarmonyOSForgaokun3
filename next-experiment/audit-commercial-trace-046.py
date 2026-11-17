# Resolve actual original ELF methods to file offsets, never guessed virtual offsets.
from pathlib import Path
import hashlib
import json
import struct
import subprocess

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / 'reports/commercial-trace-audit-046'
SOURCE = BASE / 'reports/commercial-oneway-audit-045'
LIBRARIES = {
    'service': ('librender_service.z.so', '009cb202aa11d9cb51af3b045c404038ee231883949a132ced8ea2fbaa52b654'),
    'base': ('librender_service_base.z.so', '40bd0307b161f0f46ea82d3b08e3dca7819a5c4492066f0e462b8e172e2c50c8'),
}
METHODS = [
    ('service', 'request', 'RSRenderServiceConnectionStub::OnRemoteRequest(', 'code=%x1:u32', True),
    ('service', 'register_agent', 'RSMainThread::RegisterApplicationAgent(', 'caller=%x1:u32', False),
    ('service', 'recv_parcel', 'RSUnmarshalThread::RecvParcel(', 'caller=%x3:s32 version=%x6:u32', False),
    ('service', 'cache_empty', 'RSUnmarshalThread::CachedTransactionDataEmpty(', '', True),
    ('service', 'cached_data', 'RSUnmarshalThread::GetCachedTransactionData(', '', False),
    ('service', 'commit', 'RSRenderServiceConnection::CommitTransaction(', '', False),
    ('service', 'recv_data', 'RSMainThread::RecvRSTransactionData(', '', False),
    ('service', 'process_data', 'RSMainThread::ProcessRSTransactionData(', 'caller=%x2:s32', False),
    ('service', 'process_uni', 'RSMainThread::ProcessCommandForUniRender(', '', False),
    ('service', 'request_vsync', 'RSMainThread::RequestNextVSync(', '', False),
    ('service', 'on_vsync', 'RSMainThread::OnVsync(', '', False),
    ('service', 'send_commands', 'RSMainThread::SendCommands(', '', False),
    ('base', 'unmarshal', 'RSTransactionData::Unmarshalling(', '', True),
    ('base', 'unmarshal_command', 'RSTransactionData::UnmarshallingCommand(', '', True),
]


def file_offset(data, address):
    header = struct.unpack_from('<16sHHIQQQIHHHHHH', data)
    for i in range(header[10]):
        kind, flags, offset, va, _, filesz, _, _ = struct.unpack_from(
            '<IIQQQQQQ', data, header[5] + i * header[9])
        if kind == 1 and flags & 1 and va <= address and address + 4 <= va + filesz:
            return offset + address - va
    raise AssertionError('Method not within executable file-backed PT_LOAD')


def main():
    assert not OUT.exists(), 'Preserve numbered evidence'
    data = {}
    symbols = {}
    for key, (_, digest) in LIBRARIES.items():
        path = SOURCE / (key + '.so')
        data[key] = path.read_bytes()
        assert hashlib.sha256(data[key]).hexdigest() == digest
        text = subprocess.check_output(['aarch64-linux-gnu-nm', '-D', '-C', str(path)], text=True)
        symbols[key] = [line.split(maxsplit=2) for line in text.splitlines() if ' T ' in line]
    rows = []
    for key, event, fragment, args, returns in METHODS:
        found = [row for row in symbols[key] if row[2].startswith('OHOS::Rosen::' + fragment)]
        assert len(found) == 1, (fragment, found)
        va = int(found[0][0], 16)
        offset = file_offset(data[key], va)
        assert va % 4 == offset % 4 == 0
        filename, digest = LIBRARIES[key]
        definition = 'p:commercial046/' + event + ' {root}/system/lib64/' + filename + ':' + hex(offset)
        if args:
            definition += ' ' + args
        row = dict(event=event, library=filename, sha256=digest, symbol=found[0][2],
                   virtual_address=hex(va), file_offset=hex(offset),
                   original_instruction=data[key][offset:offset + 4].hex(),
                   definition=definition, register_arguments_only=True)
        if returns:
            row['return_definition'] = 'r:commercial046/' + event + '_return {root}/system/lib64/' + filename + ':' + hex(offset) + ' value=$retval:x64'
        rows.append(row)
    OUT.mkdir()
    result = dict(probes=rows, original_elf_hashes_verified=True, executable_offsets_verified=True,
                  installed=False, runtime_verified=False, private_object_memory_read=False,
                  security_checks_modified=False, actual_desktop_verified=False)
    with (OUT / 'result.json').open('x') as out:
        json.dump(result, out, indent=2)
    print(json.dumps(dict(events=len(rows), original_elf_hashes_verified=True,
                          executable_offsets_verified=True, runtime_verified=False), indent=2))


if __name__ == '__main__':
    main()
