"""Pin the exact original ELF evidence behind the authentic caller-PID correction."""
from pathlib import Path
import hashlib
import json
import struct
import subprocess

base = Path(__file__).resolve().parents[1]
out = base / 'reports/commercial-oneway-audit-045'
image = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img')
assert not out.exists()
out.mkdir()
sources = {}
for name, origin in [('ipc', '/system/lib64/chipset-sdk-sp/libipc_single.z.so'),
                     ('service', '/system/lib64/librender_service.z.so'),
                     ('base', '/system/lib64/librender_service_base.z.so')]:
    data = subprocess.check_output(['debugfs', '-R', 'cat ' + origin, str(image)], stderr=subprocess.DEVNULL)
    assert data.startswith(b'\x7fELF\x02\x01')
    path = out / (name + '.so')
    with path.open('xb') as f:f.write(data)
    sources[name] = dict(origin=origin, sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def halfword_at_va(data, address):
    header = struct.unpack_from('<16sHHIQQQIHHHHHH', data)
    phoff, phsize, phnum = header[5], header[9], header[10]
    for index in range(phnum):
        kind, flags, offset, vaddr, paddr, filesz, memsz, align = struct.unpack_from('<IIQQQQQQ', data, phoff + index * phsize)
        if kind == 1 and vaddr <= address and address + 2 <= vaddr + filesz:
            return struct.unpack_from('<H', data, offset + address - vaddr)[0]
    raise AssertionError('Unmapped original ELF address')


service = (out / 'service.so').read_bytes()
code17 = 0x3ee540 + 4 * halfword_at_va(service, 0xdd2bc + 17 * 2)
assert code17 == 0x3f2080
ranges = [('ipc', 'commercial-invoker-receive', 0x75110, 0x75430),
          ('ipc', 'commercial-caller-pid', 0x76d14, 0x76df4),
          ('service', 'commercial-register-agent-17', code17, 0x3f21bc),
          ('service', 'commercial-transaction-receive', 0x3ee1ac, 0x3ee224),
          ('service', 'commercial-unmarshal-caller', 0x3f8e50, 0x3f8e84),
          ('base', 'commercial-profiler-pid', 0x618e94, 0x618f04)]
assembly = {}
for library, label, start, end in ranges:
    text = subprocess.check_output(['aarch64-linux-gnu-objdump', '-d', '-C',
                                    '--start-address=' + hex(start), '--stop-address=' + hex(end),
                                    str(out / (library + '.so'))], text=True)
    with (out / (label + '.asm')).open('x') as f:f.write(text)
    assembly[label] = text
assert 'ldr\tw8, [x21, #24]' in assembly['commercial-invoker-receive']
assert 'str\tw8, [x19, #12]' in assembly['commercial-invoker-receive']
assert 'ldr\tw0, [x19, #12]' in assembly['commercial-caller-pid']
assert 'IPCObjectStub::GetCallingPid()' in assembly['commercial-register-agent-17']
assert 'RSProfiler::PatchPlainPid' in assembly['commercial-register-agent-17']
assert 'mov\tw1, w20' in assembly['commercial-register-agent-17']
kernel = (base / 'reports/native-binder-kernel-031/binder.c').read_bytes()
assert b'\t\t} else {\n\t\t\ttrd->sender_pid = 0;\n\t\t}' in kernel
with (out / 'kernel031-binder.c').open('xb') as f:f.write(kernel)
result = dict(original_system_image=str(image), original_libraries=sources,
              code17_table_va=hex(0xdd2bc), code17_branch_va=hex(code17),
              kernel031_source_sha256=hashlib.sha256(kernel).hexdigest(),
              original_calls_read_sender_pid=True, sender_info_is_distinct=True,
              oneway_zero_pid_from_kernel_source=True, causal_candidate_not_runtime_pid_observation=True,
              security_checks_modified=False, original_images_written=False,
              actual_desktop_verified=False)
with (out / 'result.json').open('x') as f:json.dump(result, f, indent=2)
print(json.dumps(result, indent=2))
