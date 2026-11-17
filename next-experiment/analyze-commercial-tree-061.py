"""Correlate logged public NodeIds without treating the samples as a full tree."""
from collections import Counter, defaultdict
from pathlib import Path
import hashlib
import json
import re
import sys

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE / 'reports/commercial61-native-061'


def roots(text):
    result = []
    pattern = r'^\d\d-\d\d (\S+)\s+(\d+)\s+\d+\s+\w\s+[^/ ]+/([^/]+)/.*Rosenwindow set root, rsId:(\d+)'
    for match in re.finditer(pattern, text, re.MULTILINE):
        time, pid, app, node = match.groups()
        result.append(dict(time=time, pid=int(pid), app=app, node=int(node)))
    return result


def reachable(root, edges):
    seen = {root}
    pending = [root]
    while pending:
        for child in edges.get(pending.pop(), set()):
            if child not in seen:
                seen.add(child)
                pending.append(child)
    return seen


def main():
    evidence = ROOT / 'runtime-evidence'
    manifest = json.loads((evidence / 'retrieval-manifest.json').read_text())
    for name, item in manifest['files'].items():
        data = (evidence / 'raw' / name).read_bytes()
        assert len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256']
    hw = json.loads((ROOT / 'hwbreak-analysis.json').read_text())
    render = json.loads((ROOT / 'render-analysis.json').read_text())
    dispatch = json.loads((BASE / 'reports/commercial-command-dispatch-061/result.json').read_text())
    assert dispatch['command_template_dispatch_verified']
    assert hw['run'] == render['run'] == manifest['run']
    text = (evidence / 'raw/interactive-hilog030.log').read_text(errors='replace')
    root_rows = roots(text)
    scene_roots = {r['node'] for r in root_rows if r['app'] == 'com.ohos.sceneboard'}
    names = {int(node): name for name,node in re.findall(r'node:\[name: (.*?), id: (\d+)\]', text)}
    groups = defaultdict(list)
    for row in hw['records']:
        groups[row['event']].append(row)
    first = min(render['first_flush_guest_seconds'], default=None)
    summary = {}
    for spec in json.loads((BASE / 'reports/commercial-render-audit-061/result.json').read_text())['probes']:
        event = spec['event']
        rows = groups[event]
        summary[event] = dict(logged_samples=len(rows),
            hardware_counter_total=sum(int(r['count']) for r in hw['final_counts'] if r['event'] == event),
            postflush_logged_samples=sum(first is not None and r['ns'] >= first * 1e9 for r in rows),
            unique_node_ids=len({r['x1'] for r in rows}),
            node_namespace_high32_counts=dict(Counter(str(r['x1'] >> 32) for r in rows)))
    attaches = [dict(root=r['x1'], surface=r['x2'], surface_log_name=names.get(r['x2']),
        root_seen_in_sceneboard_log=r['x1'] in scene_roots, ns=r['ns']) for r in groups['attach_uni_surface']]
    edges = defaultdict(set)
    for row in groups['add_child']:
        edges[row['x1']].add(row['x2'])
    scene_reachable = set()
    for node in scene_roots:
        scene_reachable.update(reachable(node, edges))
    updates = {}
    for event in ['update_recording', 'update_modifier_drawcmd']:
        counts = Counter(r['x1'] for r in groups[event])
        updates[event] = [dict(node=n, logged_samples=c, reachable_from_logged_sceneboard_root=n in scene_reachable)
                          for n,c in sorted(counts.items())]
    result = dict(run=manifest['run'], verified_files=len(manifest['files']),
        roots_from_original_application_logs=root_rows, event_summary=summary,
        attaches=attaches, logged_add_child_edges=[dict(parent=p,children=sorted(c)) for p,c in sorted(edges.items())],
        drawing_updates=updates, logged_sceneboard_reachable_node_ids=sorted(scene_reachable),
        first_flush_guest_seconds=first, last_composer_frame_seconds=render['last_frame_seconds'],
        postflush_composer_frames=render['postflush_frames'], lost_samples=hw['lost_samples'],
        suppressed_sample_log_lines=hw['suppressed_sample_log_lines'],
        logged_edges_are_not_a_complete_or_current_tree=True,
        helper_entry_does_not_prove_node_lookup_or_command_success=True,
        private_object_memory_read=False, actual_desktop_verified=False)
    (ROOT / 'tree-analysis.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps({k: result[k] for k in ['run','verified_files','roots_from_original_application_logs',
        'event_summary','attaches','first_flush_guest_seconds','postflush_composer_frames',
        'lost_samples','suppressed_sample_log_lines','actual_desktop_verified']}, indent=2))


if __name__ == '__main__':
    if '--self-test' in sys.argv:
        row = roots('01-01 08:00:45.393  3394  3394 I C03900/com.ohos.sceneboard/Ace: Rosenwindow set root, rsId:14577119002626')
        assert row[0]['node'] == 14577119002626 and row[0]['app'] == 'com.ohos.sceneboard'
        assert reachable(1, {1:{2}, 2:{1,3}}) == {1,2,3}
        print('PASS: original root log parsing and bounded cyclic-edge reachability')
    else:
        main()
