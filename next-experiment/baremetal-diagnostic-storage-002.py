"""Generate a versioned diagnostic; never modify the immutable 001 source."""
import hashlib


def build_source(parent):
    expected = 'df0c06405b789187635fbf3a5cd1719e0325fb8e86dcf8493fb9e0d1fd61bfcf'
    assert hashlib.sha256(parent.encode()).hexdigest() == expected
    old = '''    char *nvme[] = {"/sbin/modprobe", "--config", "/etc/modprobe.d", "nvme", NULL};
    int status = probe("nvme", nvme, 15);'''
    new = '''    char *pcie_phy[] = {"/sbin/modprobe", "--config", "/etc/modprobe.d", "phy_qcom_qmp_pcie", NULL};
    int status = probe("pcie-phy", pcie_phy, 15);
    char *nvme[] = {"/sbin/modprobe", "--config", "/etc/modprobe.d", "nvme", NULL};
    status = status ? status : probe("nvme", nvme, 15);'''
    assert parent.count(old) == 1
    return parent.replace(old, new)
