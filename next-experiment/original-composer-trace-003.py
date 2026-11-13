"""Trace the genuine Commit return once; preserve original evaluation and errno."""
from pathlib import Path
import re
import runpy

parent = runpy.run_path(str(Path(__file__).with_name('original-composer-trace-002.py')))
HELPER = r'''
/*COMPOSER_RESULT_BEGIN*/
static int32_t composer_trace_result_003(int32_t result, const char *name)
{
    int saved = errno;
    char stage[96];
    snprintf(stage, sizeof(stage), "%s_rc_%s%lld", name, result < 0 ? "neg_" : "",
             result < 0 ? -(long long)result : (long long)result);
    composer_trace(stage);
    errno = saved;
    return result;
}
/*COMPOSER_RESULT_END*/
'''


def strip_trace(source):
    assert source.count(HELPER) == 1
    source = source.replace(HELPER, '')
    source, count = re.subn(r'return composer_trace_result_003\(\((.*?)\), "Commit"\);',
                            lambda match: 'return ' + match[1] + ';', source)
    assert count == 7
    return parent['strip_trace'](source)


def adapt(source):
    traced = parent['adapt'](source)
    start = traced.index('API Commit(')
    end = traced.index('API GetDisplayReleaseFence(', start)
    body, count = re.subn(r'return ([^;]+);',
                          lambda match: 'return composer_trace_result_003((' + match[1] + '), "Commit");',
                          traced[start:end])
    assert count == 7
    traced = traced[:start] + HELPER + body + traced[end:]
    assert strip_trace(traced) == source
    return traced
