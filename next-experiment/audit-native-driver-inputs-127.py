"""Match real 124 runtime errors to the exact native modules/firmware payload."""
from pathlib import Path
import gzip
import hashlib
import json
import re
import runpy

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'next-experiment'
BUILD=Path('/home/zoinve/harmony-virgl-883')
if __name__=='__main__':
    folder=ROOT/'reports/native-driver-inputs-127'
    assert not folder.exists()
    folder.mkdir()
    parse=runpy.run_path(str(BASE/'audit-commercial-network-inputs-079.py'))['members']
    archive=BUILD/'commercial61-native-123/initrd.img'
    manifest=json.loads((ROOT/'reports/commercial61-native-123/result.json').read_text())
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==next(row['sha256'] for row in manifest['artifacts'] if row['name']=='initrd.img')
    selected=re.compile(r'huawei_gaokun|snd[_-]|soundwire|hci_uart|btqca|bluetooth|q6apm|q6prm|qcom.*adsp|wcd93|wsa88|qcadsp|qccdsp|qcvss|/qca/')
    entries=[]
    for name,mode,data in parse(gzip.decompress(archive.read_bytes())):
        if selected.search(name):
            entries.append(dict(path=name,mode=mode,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
    retrieval=json.loads((ROOT/'reports/commercial61-native-124/runtime-evidence/retrieval-manifest.json').read_text())
    logpath=ROOT/'reports/commercial61-native-124/runtime-evidence/raw/interactive-hilog030.log'
    raw=logpath.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==retrieval['files'][logpath.name]['sha256']
    sanitize=runpy.run_path(str(BASE/'analyze-original-devicedetect-095.py'))['sanitize']
    patterns={
        'battery':rb'Battery|battery|XPower|xpower',
        'brightness':rb'backlight|Backlight|DisplayPowerMgr|Brightness|brightness',
        'audio':rb'AudioHdi|AudioHDI|AudioVdi|AudioVDI|Alsa|ALSA|audio.*adapter',
        'bluetooth':rb'bluetooth.*(?:fail|Fail)|Bluetooth.*(?:fail|Fail)|BtVendor|BT_VENDOR|Hci.*(?:fail|Fail)',
    }
    counts={key:0 for key in patterns};samples={key:[] for key in patterns}
    for number,line in enumerate(raw.splitlines(),1):
        if len(line)>4096:continue
        for key,pattern in patterns.items():
            if not re.search(pattern,line):continue
            counts[key]+=1
            # Prefer actionable failures and original driver paths over routine state spam.
            if re.search(rb'fail|Fail|error|Error|/sys/|/dev/|adapter|Adapter|[Uu]nknown|[Nn]ot found|[Nn]o such',line):
                if len(samples[key])<100:samples[key].append(dict(line=number,text=sanitize(line)))
    config=(BUILD/'native-binder-kernel-045/out/.config').read_text()
    result=dict(payload_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),payload_entries=entries,
        kernel_config=[line for line in config.splitlines() if any(key in line for key in ['CONFIG_SND_SOC_SC8280XP','CONFIG_SND_SOC_WSA883','CONFIG_SND_SOC_WCD938','CONFIG_BT_HCIUART','CONFIG_BT_QCA','CONFIG_HUAWEI_GAOKUN','CONFIG_QCOM_Q6V5_ADSP'])],
        runtime_run=retrieval['run'],runtime_hilog_sha256=retrieval['files'][logpath.name]['sha256'],counts=counts,samples=samples,
        operational_boot_performed=False,original_images_written=False)
    (folder/'result.json').open('x').write(json.dumps(result,indent=2))
    print(json.dumps(dict(payload_entries=len(entries),kernel_config=result['kernel_config'],counts=counts,first_failures={key:rows[:5] for key,rows in samples.items()}),indent=2))
