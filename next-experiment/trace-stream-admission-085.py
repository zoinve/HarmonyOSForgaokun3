"""Keep independently valid streams; explicitly report corrupt/interleaved ones."""
import re


def inspect_streams(raw):
    pattern = (rb'COMMERCIAL043_STREAM_BEGIN sample=(\d+) pid=0 path=/data/native-perf-023.trace limit=(\d+)\n'
               rb'(.*?)\nCOMMERCIAL043_STREAM_END sample=\1 pid=0 path=/data/native-perf-023.trace bytes=(\d+) eof=(\d+) errno=(\d+)')
    valid, rejected = [], []
    for match in re.finditer(pattern, raw, re.S):
        body = match[3]
        count, limit = int(match[4]), int(match[2])
        metadata = dict(sample=int(match[1]), limit=limit, bytes=count,
                        eof=int(match[5]), errno=int(match[6]))
        if len(body) != count or count > limit:
            rejected.append(dict(metadata, actual_body_bytes=len(body), reason='byte_count_or_limit_mismatch'))
            continue
        valid.append(dict(metadata, body=body))
    return dict(valid=valid, rejected=rejected)
