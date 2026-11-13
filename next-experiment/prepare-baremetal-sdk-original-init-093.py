"""Observe original AppSpawn daemon and child-tag errors; change no security checks."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-092.py')))
source = parent['source'].replace('ORIGINAL_INIT092_', 'ORIGINAL_INIT093_').replace('GRAPHICS092_', 'GRAPHICS093_')
start = source.index('static void graphics_foundation_query_078(')
end = source.index('\nstatic void ', start + 1)
original = source[start:end]
helper = original.replace('graphics_foundation_query_078', 'graphics_appspawn_query_093')
helper = helper.replace('long foundation_pid)', 'long appspawn_pid, int by_tag)')
helper = helper.replace('foundation_pid', 'appspawn_pid').replace('FOUNDATION_QUERY', 'APPSPAWN_QUERY')
helper = helper.replace('original_tool=1 tail=200\\n", sample, appspawn_pid',
                        'original_tool=1 tail=200 by_tag=%d\\n", sample, appspawn_pid, by_tag')
anchor = '        char *const args[] = {"/system/bin/hilog", "-z", "200", "-P", argument, NULL};'
assert helper.count(anchor) == 1
helper = helper.replace(anchor, '''        char *const tag_args[] = {"/system/bin/hilog", "-z", "200", "-T", "AppSpawn", NULL};
        if (by_tag) {
            execv(tag_args[0], tag_args);
            dprintf(1, "GRAPHICS093_APPSPAWN_QUERY_EXEC_ERROR errno=%d\\n", errno);
            _exit(74);
        }
''' + anchor)
source = source[:end] + '\n' + helper + source[end:]
anchor = '        long account_pid = 0;'
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + '\n        long appspawn_pid = 0;')
anchor = '                    account_pid = pid;'
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + '''
                if ((strstr(text, "/system/bin/appspawn ") == text || !strncmp(text, "appspawn ", 9)) && pid > appspawn_pid)
                    appspawn_pid = pid;''')
# Existing passive process filter already accepts appspawn through the broad original
# observer; add an explicit match rather than depending on incidental string matches.
anchor = '!strstr(text, "accountmgr")) continue;'
assert source.count(anchor) == 1
source = source.replace(anchor, '!strstr(text, "accountmgr") && !strstr(text, "appspawn")) continue;')
anchor = '            graphics_account_query_090(sample, account_pid);'
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + '''
        if ((sample == 41 || sample == 49 || sample == 61) && appspawn_pid > 1) {
            graphics_appspawn_query_093(sample, appspawn_pid, 0);
            graphics_appspawn_query_093(sample, appspawn_pid, 1);
        }''')
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-092', 'baremetal-sdk-original-init-093')
compile(payload, 'original-appspawn-observation-093-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
