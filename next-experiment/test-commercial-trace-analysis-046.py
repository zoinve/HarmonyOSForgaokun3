from pathlib import Path
import runpy

m = runpy.run_path(str(Path(__file__).with_name('analyze-commercial-trace-046.py')))
text = '''# tracer: nop
render_service-1159 [003] d..2 79.114178: recv_parcel: (0x1234) caller=3324 version=1
render_service-1159 [003] d..2 79.114178: recv_parcel: (0x1234) caller=3324 version=1
OS_IPC_0-1806 [004] .... 79.115000: unmarshal_return: (0x1234 <- 0x5678) value=0xdeadbeef
not a trace record
'''
rows = m['parse_trace'](text)
assert len(rows) == 2
assert rows[0]['global_tid'] == 1159 and rows[0]['event'] == 'recv_parcel'
assert rows[0]['arguments'] == dict(caller='3324', version='1')
assert rows[1]['arguments']['value'] == '0xdeadbeef'
assert rows[1]['comm'] == 'OS_IPC_0'
assert m['parse_trace']('trace truncated or unavailable') == []
print('PASS: real probe text, deduplication, global TID, raw return values; absent text not fabricated')
