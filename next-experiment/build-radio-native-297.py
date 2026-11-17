"""Expose the real broker through the original service's existing vendor view."""
from pathlib import Path
import runpy

BASE = Path(__file__).resolve().parent
PREVIOUS = runpy.run_path(str(BASE / 'build-radio-native-294.py'))
MODULE = PREVIOUS['MODULE']
SOCKET = '/vendor/lib64/harmony-graphics/native-bt-broker.sock'
TRACE = '/vendor/lib64/harmony-graphics/native-bt-vendor.trace'

def runtime297(text):
    text = PREVIOUS['PRIOR']['runtime285'](text)
    placeholders = '''    const char *radio297_nodes[] = {
        "/run/commercial-vendor004/upper/lib64/harmony-graphics/native-bt-broker.sock",
        "/run/commercial-vendor004/upper/lib64/harmony-graphics/native-bt-vendor.trace"};
    for (unsigned i=0;i<2;++i) {
        int node=open(radio297_nodes[i],O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);
        if (node<0 || close(node)) fail("QCA297 RAM endpoint placeholder");
    }
'''
    text = MODULE['once'](text, '    commercial_vendor016();', '    commercial_vendor016();\n' + placeholders)
    bindings = r'''    const char *radio297_sources[] = {"/native-bt-broker.sock", "/radio261/vendor.trace"};
    const char *radio297_targets[] = {
        "/vendor/lib64/harmony-graphics/native-bt-broker.sock",
        "/vendor/lib64/harmony-graphics/native-bt-vendor.trace"};
    for (unsigned i=0;i<2;++i) {
        struct stat node;
        if (lstat(radio297_sources[i],&node) || node.st_uid!=3021 ||
            (node.st_mode&0777)!=0600 || (i==0?!S_ISSOCK(node.st_mode):!S_ISREG(node.st_mode)) ||
            mount(radio297_sources[i],radio297_targets[i],NULL,MS_BIND,NULL))
            fail("QCA297 existing sandbox vendor endpoint bind");
    }
    dprintf(1,"RADIO297_SANDBOX_ENDPOINT existing_vendor_view=1 original_uid=3021 endpoint_mode=0600\n");
'''
    anchor = '    dprintf(1,' + chr(34) + 'RADIO261_ORIGINAL_HDF'
    return MODULE['once'](text, anchor, bindings + anchor)

def vendor297(source):
    return PREVIOUS['vendor294'](source).replace('/radio261/vendor.trace', TRACE)

def outer297(text, old_digest, digest):
    text = PREVIOUS['outer294'](text, old_digest, digest)
    text = text.replace('/commercial61-native-294/bootstrap-runtime087',
                        '/commercial61-native-297/bootstrap-runtime087')
    text = text.replace('RADIO294_', 'RADIO297_').replace('radio294_observe', 'radio297_observe')
    return text.replace(chr(34) + '/radio261/vendor.trace' + chr(34), chr(34) + TRACE + chr(34)).replace(
        chr(34) + '/native-bt-broker.sock' + chr(34), chr(34) + SOCKET + chr(34))

if __name__ == '__main__':
    source = (BASE / 'build-radio-native-276.py').read_text().replace('276', '297')
    begin = source.index('def vendor_trace(')
    end = source.index("if __name__ == '__main__':", begin)
    source = source[:begin] + 'vendor_trace = vendor297\n\n' + source[end:]
    source = source.replace("    once = module['once']", "    module['runtime'] = runtime297\n    once = module['once']", 1)
    source = source.replace("result = module['outer'](text, old_digest, digest)",
                            'return transform_outer297(text, old_digest, digest)', 1)
    start = source.index('        assert result.count(')
    end = source.index('    env = dict(', start)
    source = source[:start] + source[end:]
    anchor = '    env = dict('
    source = source.replace(anchor, '    source = source.replace(' + repr(repr('/native-bt-broker.sock')) +
        ', ' + repr(repr(SOCKET)) + ')\n' + anchor, 1)
    exec(compile(source, 'build-radio-native-297.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'build-radio-native-297.generated.py'),
              vendor297=vendor297, runtime297=runtime297, transform_outer297=outer297))
