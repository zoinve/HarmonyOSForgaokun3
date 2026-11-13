"""Test the missing Gaokun UCSI/HPD supplier hypothesis with one module request."""
import hashlib


def build_source(parent):
    assert hashlib.sha256(parent.encode()).hexdigest() == '194f74cfc34e07609ee7a3d21c6bb7149240b7640661a1b688803ef7ce5b3c92'
    anchor = '"huawei_gaokun_ec", '
    assert parent.count(anchor) == 1
    return parent.replace(anchor, anchor + '"ucsi_huawei_gaokun", ', 1)
