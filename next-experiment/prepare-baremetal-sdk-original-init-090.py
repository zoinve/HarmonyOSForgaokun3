"""Working canonical system tree; genuine account/Foundation logs, no audit rules."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-083.py')))
source = parent['source'].replace('ORIGINAL_INIT083_', 'ORIGINAL_INIT090_').replace('GRAPHICS083_', 'GRAPHICS090_')
old = '    if (symlink("/usr/system", "/system") || symlink("/system/etc", "/etc") ||'
assert source.count(old) == 1
source = source.replace(old, r'''    if (mkdir("/system", 0755) && errno != EEXIST) fail("original system mountpoint");
    struct stat system_st;
    if (lstat("/system", &system_st) || !S_ISDIR(system_st.st_mode))
        fail("original system requires genuine directory");
    if (mount("/usr/system", "/system", NULL, MS_BIND, NULL) ||
        mount(NULL, "/system", NULL, MS_BIND | MS_REMOUNT | MS_RDONLY | MS_NODEV, NULL))
        fail("original system readonly bind");
    char system_real[4096];
    if (!realpath("/system", system_real) || strcmp(system_real, "/system"))
        fail("original system canonical mountpoint");
    dprintf(1, "GRAPHICS090_SYSTEM_BIND source=/usr/system target=/system canonical=%s readonly=1 original_files=1\n", system_real);
    if (symlink("/system/etc", "/etc") ||''')
old = '"/system/bin/hilog", "-a", "600", "-P", argument, NULL'
assert source.count(old) == 2  # Foundation and SAMGR; preserve SAMGR head query.
start = source.index('static void graphics_foundation_query_078(')
end = source.index('\nstatic void ', start + 1)
foundation = source[start:end]
foundation = foundation.replace(old, '"/system/bin/hilog", "-z", "200", "-P", argument, NULL')
source = source[:start] + foundation + source[end:]
account = foundation.replace('graphics_foundation_query_078', 'graphics_account_query_090')
account = account.replace('foundation_pid', 'account_pid').replace('FOUNDATION_QUERY', 'ACCOUNT_QUERY')
source = source.replace(foundation, foundation + '\n' + account, 1)
anchor = '        long foundation_pid = 0;'
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + '\n        long account_pid = 0;')
anchor = '!strstr(text, "devmgr") && !strstr(text, "param_watcher")) continue;'
assert source.count(anchor) == 1
source = source.replace(anchor, '!strstr(text, "devmgr") && !strstr(text, "param_watcher") && !strstr(text, "accountmgr")) continue;')
anchor = '                    foundation_pid = pid;'
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + r'''
                if ((strstr(text, "/system/bin/accountmgr ") == text || !strncmp(text, "accountmgr ", 11)) && pid > account_pid)
                    account_pid = pid;''')
anchor = '            graphics_foundation_query_078(sample, foundation_pid);'
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + '''
        if ((sample == 24 || sample == 30 || sample == 41) && account_pid > 1)
            graphics_account_query_090(sample, account_pid);''')
assert 'AUDIT_ADD_RULE' not in source and 'fanotify_init' not in source
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-083', 'baremetal-sdk-original-init-090')
compile(payload, 'original-account-observation-090-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
