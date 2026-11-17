"""Persist boundaries around each target trace control write."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-047.py'))
inner = p['inner']
outer = p['outer'].replace('commercial61-native-047', 'commercial61-native-048').replace('COMMERCIAL047', 'COMMERCIAL048').replace('commercial047/', 'commercial048/').replace('events/commercial047', 'events/commercial048')
start = '    int fd=open(path,O_WRONLY|O_CLOEXEC);if(fd<0)return -1;'
assert outer.count(start) == 1
outer = outer.replace(start, '    dprintf(1,"COMMERCIAL048_TRACE_CONTROL_BEGIN path=%s text=%s",path,text);snapshot();\n' + start, 1)
end = '    close(fd);if(error){errno=error;return -1;}return 0;'
assert outer.count(end) == 1
outer = outer.replace(end, '    close(fd);dprintf(1,"COMMERCIAL048_TRACE_CONTROL_END path=%s error=%d\\n",path,error);snapshot();if(error){errno=error;return -1;}return 0;', 1)
payload = p['payload'].replace('outer=' + repr(p['outer']), 'outer=' + repr(outer), 1)
payload = payload.replace('commercial61-native-047', 'commercial61-native-048')
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
