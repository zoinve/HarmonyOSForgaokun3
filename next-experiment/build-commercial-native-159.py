"""Integrate verified address discovery without modifying original services."""
from pathlib import Path
import inspect
import re
import runpy

BASE = Path(__file__).resolve().parent


def adapt(source, archive_hash):
    assert source.count('#include "native-live-debug-157.h"') == 1
    assert archive_hash in source
    return source.replace('LIVE157','LIVE159').replace('native_live157','native_live159').replace('native-live-debug-157.h','native-live-debug-159.h')


def helper_source159():
    source = runpy.run_path(str(BASE / 'build-commercial-native-158.py'))['helper_source158']()
    for old, new in [('LIVE158','LIVE159'),('ROOT158','ROOT159'),('KEY158','KEY159'),
        ('ADDRESS158','ADDRESS159'),('stop158','stop159'),('context158','context159'),
        ('stop_handler158','stop_handler159'),('now158','now159'),('number158','number159'),
        ('optin158','optin159'),('bind_log158','bind_log159'),('key_copy158','key_copy159'),
        ('address158','address159'),('worker158','worker159'),('live-debug158','live-debug159'),
        ('harmony.live_debug158=1','harmony.live_debug159=1'),('--native-live158','--native-live159')]:
        source = source.replace(old,new)
    source = source.replace('#include "live-debug-root-158.h"', '#include "live-debug-root-158.h"\n#include "live-debug-address-159.h"\n#include "live-debug-discovery-159.h"',1)
    source = source.replace('#define ADDRESS159 "192.168.10.210"\n','',1)
    start = source.index('static int address159(void)')
    end = source.index('static int worker159(',start)
    source = source[:start] + '''static int address159(char address[INET_ADDRSTRLEN])
{
    struct ifaddrs *head = NULL;
    if (getifaddrs(&head)) return 0;
    int selected = live_address159_select(head,address);
    freeifaddrs(head);
    return selected == 0;
}

static int discover_loop159(int fd, unsigned index, const char *address)
{
    unsigned remaining = 32;
    time_t last_reply = 0;
    long long start = now159();
    while (!stop159) {
        long long now = now159();
        if (start < 0 || now < start || now - start >= 90000) break;
        struct pollfd item = {.fd=fd,.events=POLLIN};
        if (poll(&item,1,100) > 0 && discovery159_step(fd,index,address,&remaining,&last_reply) < 0) return 102;
    }
    close(fd);
    return 0;
}

''' + source[end:]
    source = source.replace('    while (!address159()) {','    char address[INET_ADDRSTRLEN];\n    while (!address159(address)) {',1)
    anchor = '    if (bind_log159(196,ROOT159 "/logs/hilog")'
    assert source.count(anchor) == 1
    source = source.replace(anchor,'''    if (live_address159_config(ROOT159 "/etc/ssh/sshd_config",ROOT159 "/etc/ssh/sshd_config.live",address)) return 100;
    int discovery = discovery159_open("wlan0");
    unsigned interface_index = if_nametoindex("wlan0");
    if (discovery < 0 || !interface_index) return 101;
''' + anchor,1)
    source = source.replace('address=" ADDRESS159 " port=22257\\n",','address=%s port=22257 discovery_port=22259\\n",',1)
    source = source.replace('context->target,(unsigned long long)context->net_inode);','context->target,(unsigned long long)context->net_inode,address);',1)
    source = source.replace('    if (!daemon) {','    if (!daemon) {\n        close(discovery);',1)
    source = source.replace('"/etc/ssh/sshd_config",NULL','"/etc/ssh/sshd_config.live",NULL',1)
    anchor = '    dprintf(1,"LIVE159_SERVER_SPAWNED'
    assert source.count(anchor) == 1
    source = source.replace(anchor,'''    pid_t discoverer = fork();
    if (discoverer < 0) return 103;
    if (!discoverer) _exit(discover_loop159(discovery,interface_index,address));
    close(discovery);
''' + anchor,1)
    assert 'ADDRESS159' not in source and '192.168.10.210' not in source
    assert 'live_root158_open' in source
    return source


if __name__ == '__main__':
    source = (BASE / 'build-commercial-native-157.py').read_text()
    assert not re.search(r'[0-9a-f]{64}',source), 'never transform literal hashes'
    source = source.replace('157','159').replace('commercial61-native-153','commercial61-native-157')
    source = source.replace('reports/live-debug-inputs-159','reports/live-debug-inputs-157')
    start = source.index('def adapt(')
    end = source.index("\n\nif __name__ == '__main__':",start)
    source = source[:start] + inspect.getsource(adapt) + '\n\n' + inspect.getsource(helper_source159) + source[end:]
    source = source.replace('import runpy\n','import runpy\n',1)
    anchor = '    work.mkdir();report.mkdir()'
    addition = '''
    fixture = json.loads((ROOT / 'reports/live-debug-discovery-159-compile-fix-1/result.json').read_text())
    assert fixture['network_discovery_fixture_pass'] and fixture['remote']['listener_absent']
    for name, digest in fixture['sources'].items():
        assert sha((BASE / name).read_bytes()) == digest, 'verified discovery source changed'
    helper_source = helper_source159()
    (work / 'live-debug-launcher-159.c').open('x').write(helper_source)
    header_source = (BASE / 'native-live-debug-157.h').read_text().replace('157','159').replace('live-debug-inputs-159','live-debug-inputs-157')
    (work / 'native-live-debug-159.h').open('x').write(header_source)
'''
    assert source.count(anchor) == 1
    source = source.replace(anchor,anchor + '\n' + addition,1)
    source = source.replace("BASE / 'live-debug-launcher-159.c'","work / 'live-debug-launcher-159.c'")
    source = source.replace("BASE / 'native-live-debug-159.h'","work / 'native-live-debug-159.h'")
    anchor = "'-Werror',str(work / 'live-debug-launcher-159.c')"
    assert source.count(anchor) == 1
    source = source.replace(anchor,"'-Werror','-I',str(BASE),str(work / 'live-debug-launcher-159.c')",1)
    exec(compile(source,'build-commercial-native-159.generated.py','exec'),
        {'__name__':'__main__','__file__':str(BASE / 'build-commercial-native-159.generated.py')})
