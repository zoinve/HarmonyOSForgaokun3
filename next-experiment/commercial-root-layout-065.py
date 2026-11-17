"""Restore the original image's chipset alias, not new permissions or flags."""
FIX = r'''
static void commercial_original_layout065(void)
{
    char target[64];
    ssize_t length=readlink("/usr/chipset",target,sizeof(target));
    if(length!=7 || memcmp(target,"/vendor",7))fail("original chipset alias mismatch");
    struct stat st,original;
    if(!lstat("/chipset",&st) || errno!=ENOENT)fail("chipset alias must be absent");
    if(symlink("/vendor","/chipset"))fail("original chipset alias restore");
    if(stat("/chipset/etc/param",&st) || stat("/vendor/etc/param",&original) ||
       st.st_dev!=original.st_dev || st.st_ino!=original.st_ino || !S_ISDIR(st.st_mode))
        fail("original chipset parameter directory identity");
    dprintf(1,"COMMERCIAL065_ROOT_LAYOUT path=/chipset target=/vendor original_link_matched=1 permission_rules_unmodified=1\n");
}
'''
CALL = '    commercial_original_layout065();\n'


def repair(inner):
    anchor = '    directory("/data", 0755);\n    volatile_ext4_data_037();'
    assert inner.count(anchor) == 1
    assert inner.count('int main(void)') == 1
    assert 'commercial_original_layout065' not in inner
    return inner.replace('int main(void)', FIX + '\nint main(void)', 1).replace(anchor, CALL + anchor, 1)
