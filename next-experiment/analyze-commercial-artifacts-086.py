"""Admit exact event byte streams and structured original UI layout snapshots."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def event_files(raw):
    phase_pattern = (rb'^PHASE_BEGIN wifi-supplicant-(?P<mode>start|events)086\n(.*?)'
                     rb'^PHASE_END wifi-supplicant-(?P=mode)086 status=(-?\d+)[ \t]*$')
    rows = []
    for match in re.finditer(phase_pattern, raw, re.MULTILINE | re.DOTALL):
        mode, body, status = match.groups()
        context = re.search(rb'^NETWORK084_TARGET_CONTEXT pid=(\d+) net_inode=(\d+) mnt_inode=(\d+) pid_inode=(\d+) root_verified=1 mode=' + mode + rb' connectivity_not_inferred=1$', body, re.MULTILINE)
        rows.append((mode, body, int(status), context.groups() if context else None))
    starts = {context for mode, body, status, context in rows if mode == b'start' and status == 0 and context}
    files, rejected, seen = [], [], set()
    pattern = (rb'^EVENT086_FILE_BEGIN name=(THREAD_BLOCK_[A-Za-z0-9_.-]+\.log) size=(\d+)\n(.*?)'
               rb'^\nEVENT086_FILE_END name=\1 bytes=(\d+) eof=([01]) errno=(\d+) full_file_not_inferred=1$')
    for mode, output, status, context in rows:
        if mode != b'events' or status != 0 or context not in starts:
            continue
        for match in re.finditer(pattern, output, re.MULTILINE | re.DOTALL):
            name, size, body, count, eof, error = match.groups()
            digest = hashlib.sha256(body).hexdigest()
            key = (name, digest)
            if key in seen:
                continue
            seen.add(key)
            row = dict(name=name.decode('ascii'), size_before=int(size), captured_bytes=int(count),
                       eof=int(eof), errno=int(error), captured_sha256=digest)
            if len(body) != int(count) or int(count) > 1048576:
                rejected.append(dict(row, actual_body_bytes=len(body), reason='byte_count_or_limit_mismatch'))
                continue
            row['complete_read_observed_not_writer_completion'] = int(error) == 0 and int(eof) == 1 and int(size) == int(count)
            files.append(dict(row, body=body))
    return dict(files=files, rejected=rejected)


def layout_nodes(value):
    pending, attributes = [(value, 0)], []
    visited = 0
    while pending:
        node, depth = pending.pop()
        visited += 1
        if visited > 100000 or depth > 128:
            raise ValueError('layout traversal bound exceeded')
        if isinstance(node, dict):
            attr = node.get('attributes')
            if isinstance(attr, dict):
                keep = {key: attr[key] for key in ('text', 'type', 'id', 'key', 'bundleName', 'bounds', 'clickable', 'enabled', 'visible', 'focused') if key in attr}
                attributes.append(keep)
            pending.extend((item, depth + 1) for item in node.values() if isinstance(item, (dict, list)))
        elif isinstance(node, list):
            pending.extend((item, depth + 1) for item in node if isinstance(item, (dict, list)))
    return attributes


def main():
    folder = ROOT / 'reports/commercial61-native-086'
    raw = folder / 'runtime-evidence/raw'
    manifest = json.loads((raw.parent / 'retrieval-manifest.json').read_text())
    for name, row in manifest['files'].items():
        blob = (raw / name).read_bytes()
        assert len(blob) == row['bytes'] and hashlib.sha256(blob).hexdigest() == row['sha256']
    phase = max(raw.glob('phase-*.log'), key=lambda path: int(path.stem.split('-')[1]))
    blob = phase.read_bytes()
    recovered = event_files(blob)
    destination = folder / 'original-eventlogs'
    destination.mkdir(exist_ok=False)
    saved = []
    for row in recovered['files']:
        body = row['body']
        name = row['name'] + '.' + row['captured_sha256'][:16] + '.capture'
        assert Path(name).name == name
        with (destination / name).open('xb') as stream:
            stream.write(body)
        saved.append(dict({key: value for key, value in row.items() if key != 'body'}, saved_as=name))
    script_log = raw / 'snapshot075-commercial-desktop086.log'
    script_text = script_log.read_text(errors='replace') if script_log.exists() else ''
    layouts = []
    for target in (100, 130):
        name = f'snapshot075-native-layout086-{target}.json'
        path = raw / name
        row = dict(target=target, file=name, file_retrieved=path.exists(),
                   original_tool_reported_exit0=bool(re.search(r'^LAYOUT086_RESULT target=' + str(target) + r' exit_status=0 success_not_inferred=1$', script_text, re.MULTILINE)))
        if path.exists():
            data = path.read_bytes()
            row.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
            try:
                value = json.loads(data)
                attributes = layout_nodes(value)
                row.update(json_valid=True, node_count=len(attributes), attributes=attributes,
                           visible_text=list(dict.fromkeys(str(item['text']) for item in attributes if item.get('text'))))
            except (ValueError, UnicodeError, RecursionError) as exc:
                row.update(json_valid=False, parse_error=str(exc))
        layouts.append(row)
    result = dict(run=manifest['run'], verified_files=len(manifest['files']), source_phase=phase.name,
                  source_phase_sha256=hashlib.sha256(blob).hexdigest(),
                  captured_eventlogs=saved, rejected_eventlog_streams=recovered['rejected'],
                  layout_diagnostic_log_retrieved=script_log.exists(), layout_records=layouts,
                  original_ui_layout_proven=any(row.get('json_valid') and row.get('node_count', 0) > 0 and row['original_tool_reported_exit0'] for row in layouts),
                  oobe_completed_proven=False, desktop_visible_interaction_proven=False)
    with (folder / 'native-artifact-analysis.json').open('x') as stream:
        json.dump(result, stream, indent=2, ensure_ascii=True)
    print(json.dumps({key: value for key, value in result.items() if key != 'layout_records'}, indent=2))
    for row in layouts:
        print(json.dumps({key: value for key, value in row.items() if key != 'attributes'}, ensure_ascii=True))


if __name__ == '__main__':
    main()
