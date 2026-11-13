"""Apply the audited board supplier list to immutable generated 002 source."""
import hashlib


def build_source(parent):
    assert hashlib.sha256(parent.encode()).hexdigest() == 'ecc18f7d23ac94dbd46a031938e7cb2ac6be95eab6ce394c1c661c189ac765c5'
    old = 'const char *modules[] = {"huawei_gaokun_ec", "panel_himax_hx83121a", "msm", "i2c_hid_of"};'
    new = 'const char *modules[] = {"i2c_qcom_geni", "huawei_gaokun_ec", "qcom_refgen_regulator", "panel_himax_hx83121a", "msm", "spi_geni_qcom", "himax_hx83121a_spi"};'
    assert parent.count(old) == 1
    return parent.replace(old, new)
