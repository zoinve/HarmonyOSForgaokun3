"""Export only privacy-scanned manifest members, preserving damaged entries."""
from pathlib import Path
import runpy

BASE = Path(__file__).resolve().parent
REPORT = BASE.parent / 'reports/commercial61-native-235'

if __name__ == '__main__':
    assert (REPORT / 'post-return-verification.json').is_file()
    assert not (REPORT / 'runtime-evidence').exists()
    source = (REPORT / 'partial-retrieval-240.generated.py').read_text()
    old = " subprocess.run(['tar','-C',str(run),'-cf','-','.'],check=True)"
    assert source.count(old) == 1
    source = source.replace(old, " subprocess.run(['tar','-C',str(run),'-cf','-','--',*files],check=True)")
    old = "manifest['successful_cumulative_snapshots_retained']=2"
    assert source.count(old) == 1
    source = source.replace(old, "manifest['successful_cumulative_snapshots_retained']=sum(name.startswith('phase-') for name in manifest['files'])\nmanifest['unreadable_directory_entry_observed']='phase-207.log'\nmanifest['complete_directory_export']=False")
    (REPORT / 'readable-retrieval-241.generated.py').open('x').write(source)
    runpy.run_path(str(BASE / 'commercial-workflow-235.py'))['configure_local_transport']()
    exec(compile(source, 'readable-retrieval-241', 'exec'), {'__name__': '__main__', '__file__': str(BASE / 'readable-retrieval-241.py')})
