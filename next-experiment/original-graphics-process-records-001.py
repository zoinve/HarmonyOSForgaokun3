"""Classify real argv tokens, never service names from interleaved kernel messages."""
import re


def extract_process_pids(raw, prefix, name):
    found = set()
    for pid, command in re.findall(re.escape(prefix) + rb'PROCESS sample=\d+ pid=(\d+) cmd=([^\r\n]*)', raw):
        tokens = command.split(b'[', 1)[0].split()
        if not tokens:
            continue
        executable = tokens[0].rsplit(b'/', 1)[-1]
        expected = name.encode()
        matched = executable == expected
        if executable == b'hdf_devhost' and name in ('composer_host', 'allocator_host'):
            matched = any(tokens[i:i+2] == [b'-n', expected] for i in range(1, len(tokens)-1))
        if matched:
            found.add(int(pid))
    return sorted(found)
