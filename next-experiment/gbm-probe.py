"""Repair only the omitted GBM backend's runtime search path."""
def gbm_probe(source):
    anchor = 'setenv("EGL_LOG_LEVEL","debug",1);'
    assert source.count(anchor) == 1
    source = source.replace(anchor, anchor + '\n        setenv("GBM_BACKENDS_PATH","/system/lib64/lab-softpipe-167/gbm",1);')
    anchor = ':/system/lib64/lab-softpipe-167",NULL};'
    assert source.count(anchor) == 1
    return source.replace(anchor, ':/system/lib64/lab-softpipe-167","GBM_BACKENDS_PATH=/system/lib64/lab-softpipe-167/gbm",NULL};')
