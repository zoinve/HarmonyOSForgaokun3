"""One reversible visual-effect change, restricted to the copied RAM config."""


def disable_blur(source):
    anchor = r'\"load_persist_params \", '
    assert source.count(anchor) == 1, 'expected one persistent-parameter load'
    setting = r'\"setparam persist.sys.graphic.blurEnabled 0\", '
    assert setting not in source
    return source.replace(anchor, anchor + setting, 1)
