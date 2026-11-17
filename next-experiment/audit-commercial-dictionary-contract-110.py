"""Seal the original decoder contract and the actual historical text gap."""
from pathlib import Path
import hashlib
import json
import re
import runpy
import struct
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
tools = runpy.run_path(str(BASE / 'audit-commercial-hilog-110.py'))


if __name__ == '__main__':
    out = tools['OUT'] / 'dictionary-contract'
    assert not out.exists()
    library = ROOT / 'reports/memmgr-initialization-audit-109/libmemmgrservice.z.so'
    data = library.read_bytes()
    assert hashlib.sha256(data).hexdigest() == '2cf2566bb7bf580513e82c6d1819775886cfe3ecd35a5e2b14a0eae60dceb012'
    sections = tools['sections'](data)
    note = sections['.note.gnu.build-id']
    name_size, description_size, kind = struct.unpack_from('<III', note)
    assert kind == 3 and note[12:12 + name_size] == b'GNU\0'
    offset = 12 + ((name_size + 3) // 4) * 4
    build_id = note[offset:offset + description_size]
    assert len(build_id) == 16
    uuid = int.from_bytes(build_id[:4], 'little')
    assert uuid == 3036376538
    expected = '/data/log/dict/' + build_id.hex()[:2].upper() + '/' + build_id.hex()[2:].upper()
    assert expected in (BASE / 'commercial-memmgr-dictionary-110.sh').read_text()
    evidence = ROOT / 'reports/commercial61-native-108/runtime-evidence'
    manifest = json.loads((evidence / 'retrieval-manifest.json').read_text())
    log = (evidence / 'raw/interactive-hilog030.log').read_bytes()
    digest = hashlib.sha256(log).hexdigest()
    assert digest == manifest['files']['interactive-hilog030.log']['sha256']
    unknown = re.findall(rb'^.*?/memmgrservice/MM: OpenUuidFile fail, unknown log, uuid is: (\d+)\r?$', log, re.M)
    assert str(uuid).encode() in unknown
    out.mkdir()
    ranges = [('cli-handler', tools['OUT'] / '0-hilog', 0xf0bc, 0xf2ac),
              ('daemon-handler', tools['OUT'] / 'daemon/hilogd', 0x291a4, 0x2928c),
              ('decoder-open-uuid', tools['OUT'] / '3-libhilog.so', 0x22be0, 0x23350)]
    hashes = {}
    for name, elf, start, end in ranges:
        body = subprocess.check_output(['aarch64-linux-gnu-objdump', '-d', '-C',
            '--start-address=' + hex(start), '--stop-address=' + hex(end), str(elf)])
        (out / (name + '.disassembly.txt')).open('xb').write(body)
        hashes[name] = hashlib.sha256(body).hexdigest()
    later = ROOT / 'reports/commercial61-native-109/runtime-evidence'
    later_manifest = json.loads((later / 'retrieval-manifest.json').read_text())
    later_log = (later / 'raw/interactive-hilog030.log').read_bytes()
    later_digest = hashlib.sha256(later_log).hexdigest()
    assert later_digest == later_manifest['files']['interactive-hilog030.log']['sha256']
    decoded = [line for line in later_log.splitlines() if b'/memmgrservice/MM:' in line and b'OpenUuidFile fail' not in line]
    assert any(b'OnStart init failed' in line for line in decoded)
    result = dict(service_library_sha256=hashlib.sha256(data).hexdigest(),
        original_build_id=build_id.hex(), original_hilog_uuid=uuid,
        expected_original_dictionary_path=expected,
        original_hilog_section_bytes=len(sections['_hilog_']),
        original_hilog_section_sha256=hashlib.sha256(sections['_hilog_']).hexdigest(),
        historical_log_sha256=digest, matching_unknown_message_count=unknown.count(str(uuid).encode()),
        historical_failed_lines_do_not_preserve_format_id_or_encoded_arguments=True,
        historical_recovered_message_count=0,
        experiment109_log_sha256=later_digest,
        experiment109_already_decoded_memory_message_count=len(decoded),
        dictionary_observer_deferred_as_unnecessary_for_current_failure=True,
        source_elf_to_original_dictionary_mapping_verified=True,
        original_single_elf_generation_command='/system/bin/hilog -d /system/lib64/libmemmgrservice.z.so',
        daemon_validates_elf_before_generation=True,
        cli_zero_exit_not_generation_success=True,
        actual_dictionary_generated=False, target_boot_performed=False,
        disassembly_sha256=hashes)
    (out / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
