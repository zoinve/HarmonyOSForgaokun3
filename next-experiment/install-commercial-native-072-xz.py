"""Resume the space-refused staging transaction without replacing its evidence."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
workflow = runpy.run_path(str(b / 'commercial-workflow-072.py'))
source = workflow['source072']('install-commercial-native')
source = source.replace('minimal-overlay.img', 'minimal-overlay-xz.img').replace(
    'overlay-result.json', 'overlay-result-xz.json')
source = source.replace("assert not root.exists();root.mkdir()",
    "assert root.is_dir() and (root/'installation-journal.json').is_file() and not (root/'installation-result.json').exists()")
source = source.replace("(root/'installation-journal.json').open('x')", "(root/'installation-journal-xz.json').open('x')")
anchor = "for n,data in payload.items():\n with (root/n).open('xb') as f:f.write(base64.b64decode(data));f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o755 if n!='initrd.img' else 0o600)"
assert source.count(anchor) == 1
source = source.replace(anchor, """previous_journal=json.loads((root/'installation-journal.json').read_text())
assert previous_journal['efi_before']==before and previous_journal['firmware']==firmware
for n,data in payload.items():
 blob=base64.b64decode(data,validate=True)
 if n!='initrd.img':
  assert (root/n).read_bytes()==blob
  continue
 import gzip,lzma
 assert lzma.decompress(blob)==gzip.decompress((root/'initrd.img').read_bytes())
 with (root/'initrd-xz.img').open('xb') as f:f.write(blob);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o600)""", 1)
# Subsequent transfer and admission checks must use the new compressed file.
start = source.index('guards=[]')
source = source[:start] + source[start:].replace("root/'initrd.img'", "root/'initrd-xz.img'")
source = source.replace("report/'installation.stdout'", "report/'installation-xz.stdout'").replace(
    "report/'installation.stderr'", "report/'installation-xz.stderr'")
if __name__ == '__main__':
    workflow['configure_local_transport']()
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
