from pathlib import Path
import runpy

source = runpy.run_path(str(Path(__file__).with_name('analyze-commercial-hwbreak-052.py')))['source']
source = source.replace('commercial61-native-052', 'commercial61-native-053').replace('COMMERCIAL052', 'COMMERCIAL053')
anchor = 'event_summary=summary, records=records,'
assert source.count(anchor) == 1
source = source.replace(anchor, "event_summary=summary, records=records, decode_results=dict(Counter('non_null' if row['x0'] else 'null' for row in records if row['event']=='unmarshal_result')), processing_callers=dict(Counter(str(row['x2'] & 0xffffffff) for row in records if row['event']=='process_data')),")
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
