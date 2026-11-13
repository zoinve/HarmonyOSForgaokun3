"""Add only 032 initrd/entry, sharing verified 031 kernel/DTB. Delete nothing."""
from pathlib import Path
import runpy,ast,json,subprocess
base=Path(__file__).resolve().parent.parent
source=runpy.run_path(str(base/'next-experiment/install-native-original-graphics-boot-031.py'))['source']
node=next(n for n in ast.parse(source).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PAYLOAD' for t in n.targets))
payload=ast.literal_eval(node.value)
payload=payload.replace('native-original-graphics-boot-031','native-original-graphics-boot-032')
# The 032 destination is new; kernel/DTB references deliberately stay at 031.
payload=payload.replace("entry=esp/'loader/entries/native-original-graphics-031.conf';dest=esp/'native-original-graphics-031'", "entry=esp/'loader/entries/native-original-graphics-032.conf';dest=esp/'native-original-graphics-032'")
payload=payload.replace("entry.parent.glob('native-original-graphics-031*')","entry.parent.glob('native-original-graphics-032*')")
start=payload.index('# Only two obsolete,')
end=payload.index('dest.mkdir()',start)
payload=payload[:start]+r'''
shared=esp/'native-original-graphics-031'
assert (esp/'loader/entries/native-original-graphics-030.conf').is_file()
assert (esp/'loader/entries/native-original-graphics-031.conf').is_file()
assert sha(shared/'linux')==sha(root/'linux')=='6fa44a5f1996a82bc95e8c44b3d32a69cc14d3789e39cffa2fcafafb7c294ff5'
assert sha(shared/'sc8280xp-huawei-gaokun3.dtb')==sha(root/'sc8280xp-huawei-gaokun3.dtb')=='5f6b1fa73d8bffa1984710d52c0babc4df297cbb90d9f4d9a48a433a104fb016'
obsolete=[]
# Only an initrd is added: retain >32 MiB free and every existing EFI file.
assert shutil.disk_usage(esp).free>(root/'initrd.img').stat().st_size+32*1024**2
save(root/'installation-journal.json',dict(efi_before=before,loader_before=loader,firmware_before=efi,
 deleted_obsolete_kernel_caches=[],shared_kernel=str(shared/'linux'),reserve_bytes=32*1024**2))
''' +payload[end:]
start=payload.index("with (root/'sc8280xp-huawei-gaokun3.dtb').open('rb')")
end=payload.index("options='rdinit=/init",start)
payload=payload[:start]+payload[end:]
payload=payload.replace('title HarmonyOS 031 - Binder PID FIX - NO AUTO REBOOT','title HarmonyOS 032 - Touchpad cursor - NO AUTO REBOOT')
payload=payload.replace("'initrd /native-original-graphics-031/initrd.img'","'initrd /native-original-graphics-032/initrd.img'")
assert '.unlink(' not in payload and 'set-oneshot' not in payload
if __name__=='__main__':
    report=base/'reports/native-original-graphics-boot-032/install-result.json'
    assert not report.exists() and not report.with_suffix('.stdout').exists()
    r=subprocess.run(['ssh','matebook','sudo -n python3 -'],input=payload,text=True,capture_output=True,timeout=300)
    report.with_suffix('.stdout').write_text(r.stdout,encoding='utf-8')
    report.with_suffix('.stderr').write_text(r.stderr,encoding='utf-8')
    r.check_returncode()
    with report.open('x',encoding='utf-8') as f:json.dump(json.loads(r.stdout),f,indent=2)
    print(r.stdout)
