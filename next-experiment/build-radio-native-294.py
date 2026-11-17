"""Bounded original-service diagnostics, without changing the Bluetooth ABI."""
from pathlib import Path
import runpy

BASE = Path(__file__).resolve().parent
MODULE = runpy.run_path(str(BASE / 'build-radio-native-261.py'))
PRIOR = runpy.run_path(str(BASE / 'build-radio-native-285.py'))

def vendor294(source):
    once = MODULE['once']
    source = source.replace('/data/native-bt-020.trace', '/radio261/vendor.trace')
    source = once(source, '    (void)address;', '    trace("initialize_entry",0);\n    (void)address;')
    source = once(source, '    callbacks=cb;return 0;', '    callbacks=cb;trace("initialize_ok",0);return 0;')
    source = once(source, '    if(!callbacks){', '    trace("operation_entry",(int)opcode);\n    if(!callbacks){')
    source = once(source, 'if(fd<0)return -1;', 'if(fd<0){trace("socket_create",-1);return -1;}')
    return source

def outer294(text, old_digest, digest):
    source = MODULE['outer'](text, old_digest, digest)
    source = source.replace('/commercial61-native-261/bootstrap-runtime087',
                            '/commercial61-native-294/bootstrap-runtime087')
    source = PRIOR['trace_outer285'](source)
    helper = (BASE / 'native-bt-observe-294.h').read_text()
    source = MODULE['once'](source, 'static void native_original(void)\n{',
                            helper + '\nstatic void native_original(void)\n{')
    return MODULE['once'](source, '                if(i==4 && started083)native_live159_start(child);',
        '                if(i==2 || i==4 || i==7)radio294_observe(child);\n'
        '                if(i==4 && started083)native_live159_start(child);')

if __name__ == '__main__':
    source = (BASE / 'build-radio-native-276.py').read_text().replace('276', '294')
    begin = source.index('def vendor_trace(')
    end = source.index("if __name__ == '__main__':", begin)
    source = source[:begin] + 'vendor_trace = vendor294\n\n' + source[end:]
    source = source.replace("    once = module['once']", "    module['runtime'] = runtime294\n    once = module['once']", 1)
    source = source.replace("result = module['outer'](text, old_digest, digest)",
                            'return transform_outer294(text, old_digest, digest)', 1)
    # The wrapper now delegates the full outer transformation above.
    start = source.index('        assert result.count(')
    end = source.index('    env = dict(', start)
    source = source[:start] + source[end:]
    exec(compile(source, 'build-radio-native-294.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'build-radio-native-294.generated.py'),
              vendor294=vendor294, runtime294=PRIOR['runtime285'], transform_outer294=outer294))
