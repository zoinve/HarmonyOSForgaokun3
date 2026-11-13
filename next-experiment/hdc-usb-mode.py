def hdc_usb_mode(source):
    anchor=r'\"setparam persist.hdc.mode.tcp enable\", '
    assert source.count(anchor)==1
    return source.replace(anchor,r'\"setparam persist.hdc.mode.usb disable\", '+anchor)
