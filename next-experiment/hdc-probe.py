"""Enable only the original HDC TCP trigger; observe, never defeat authentication."""
def hdc_probe(source):
    if 'hdc918-status' in source:
        return source
    anchor=r'\"load_persist_params \", '
    assert source.count(anchor)==1
    source=source.replace(anchor,anchor+r'\"setparam persist.hdc.mode.tcp enable\", ')
    anchor='    direct916();'
    assert source.count(anchor)==1
    query='param get const.security.developermode.state; param get const.hdc.secure; param get persist.hdc.mode.tcp; param get persist.hdc.control; ps -A | grep hdcd; cat /proc/net/tcp'
    return source.replace(anchor,'    lab_shell_run("hdc918-status","'+query+'",15,"/system/bin/sh");\n'+anchor)
