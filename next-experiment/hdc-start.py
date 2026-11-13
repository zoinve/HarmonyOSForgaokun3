"""Use the original init service definition; leave daemon checks untouched."""
def hdc_start(source):
    anchor = r'\"setparam net.tcp.default_init_rwnd 60\"'
    addition = r', \"start hdcd\"'
    if anchor + addition in source:
        return source
    assert source.count(anchor) == 1
    return source.replace(anchor, anchor + addition)
