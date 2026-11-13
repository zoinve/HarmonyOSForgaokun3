"""Target-only gaokun3 QCA firmware/driver bring-up before service integration."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-native-original-graphics-boot-020.py'))
inner=p['inner'];capture=p['capture']
outer=p['outer'].replace('native-original-020-%s','native-original-021-%s')
anchor='    int ash=open("/hmos_ashmem.ko",O_RDONLY|O_CLOEXEC);'
assert outer.count(anchor)==1
outer=outer.replace(anchor,r'''
    char *qca_power[]={"/sbin/modprobe","--config","/etc/modprobe.d","pwrseq_qcom_wcn",NULL};
    char *qca_uart[]={"/sbin/modprobe","--config","/etc/modprobe.d","hci_uart",NULL};
    int power_status=probe("qca-power",qca_power,10);
    int uart_status=probe("qca-uart",qca_uart,10);
    char *qca_reset[]={"/native-qca-probe-021",NULL};
    int reset_status=probe("qca-hci-reset",qca_reset,20);
    dprintf(1,"NATIVE_QCA021 power_status=%d uart_status=%d reset_status=%d original_vendor_still_fail_closed=1\n",power_status,uart_status,reset_status);
'''+anchor)
payload=p['payload'];offset=payload.index('from pathlib import Path\nimport gzip,hashlib')
prefix=payload[:offset];wrapper=prefix[prefix.index('WRAPPER=')+len('WRAPPER='):prefix.index('\nCAPTURE=')]
payload='inner='+repr(inner)+'\nouter='+repr(outer)+'\nWRAPPER='+wrapper+'\nCAPTURE='+repr(capture)+'\n'+payload[offset:]
payload=payload.replace('native-original-graphics-boot-020','native-original-graphics-boot-021')
extra=r'''
fw=root/'native-qca-firmware-021'
directory('lib/firmware/qca')
rows=json.loads((fw/'result.json').read_text())
for row in rows:
 src=fw/row['name'];assert sha(src)==row['sha256'] and src.stat().st_size==row['bytes']
 file('lib/firmware/qca/'+row['name'],src)
probe_source=project/'next-experiment/native-qca-probe-021.c'
probe_binary=work/'native-qca-probe-021'
run(['aarch64-linux-gnu-gcc','-static','-O2','-Wall','-Wextra','-Werror',str(probe_source),'-o',str(probe_binary)])
file('native-qca-probe-021',probe_binary,0o755)
with (local/'qca-bringup.json').open('x') as f:
 json.dump(dict(firmware=rows,probe_source_sha256=sha(probe_source),probe_sha256=sha(probe_binary),reference='https://github.com/right-0903/linux-gaokun',device_tree_replaced=False,transport_bridge_installed=False,ubuntu_modules_modified=False),f,indent=2)
'''
anchor="file('init',work/'init',0o755)"
assert payload.count(anchor)==1
payload=payload.replace(anchor,extra+'\n'+anchor)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
