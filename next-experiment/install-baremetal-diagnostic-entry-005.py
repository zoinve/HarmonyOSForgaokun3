"""Install a single independent identity-kernel diagnostic 008, never select or reboot."""
from pathlib import Path
import ast

def launcher_source():
    source=Path(__file__).with_name('install-baremetal-diagnostic-entry-001.py').read_text()
    changes={
        'baremetal-boot-entry-preflight-001.json':'baremetal-boot-entry-preflight-005.json',
        'baremetal-boot-entry-installed-001.json':'baremetal-boot-entry-installed-005.json',
        'boot-entry-install-001':'boot-entry-install-005',
        'harmony-native-diag-004':'harmony-native-diag-008',
        'native-diagnostic-init-004/':'native-identity-diagnostic-008/',
        'native-build-001/artifacts/arch/arm64/boot/Image':'native-identity-diagnostic-008/linux',
        'native-build-001/artifacts/arch/arm64/boot/dts/qcom/sc8280xp-huawei-gaokun3.dtb':'native-identity-diagnostic-008/sc8280xp-huawei-gaokun3.dtb',
        'f304d26414e27122716d8b6199c0d096bb314d80dc5f32fa3300dd97420523d0':'8ba8c0049c3608e3a72769897e718051c78addb4d73a29699714f2e49f576457',
        '884772104ac2f858697a1730d0f8307db05a9155c3b677355f881c1939b120e1':'58159556c88dc79ca32adf15aa386dd320e18403d33b32de9c7480705761d2fe',
        'native hardware diagnostic 004':'native identity and hardware diagnostic 008',
    }
    for old,new in changes.items():assert old in source,old;source=source.replace(old,new)
    ast.parse(source);return source

if __name__=='__main__':exec(compile(launcher_source(),__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})
