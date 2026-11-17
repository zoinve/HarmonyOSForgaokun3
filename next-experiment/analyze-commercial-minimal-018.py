"""Hash-checked 018 results, retaining full evidence without a desktop assumption."""
from pathlib import Path
source=Path(__file__).with_name('analyze-commercial-minimal-017.py').read_text()
source=source.replace('commercial61-native-017','commercial61-native-018').replace('COMMERCIAL017','COMMERCIAL018')
source=source.replace("['sceneboard','render_service','composer_host','allocator_host']","['sceneboard','render_service','composer_host','allocator_host','appspawn']")
source=source.replace("with (root/'runtime-analysis.json')", "data['appspawn_evidence']=[l for l in (s+'\\n'+f).splitlines() if ('appspawn' in l.lower() and any(x in l.lower() for x in ['exit','serviceexec','started','fail']))][-80:]\nwith (root/'runtime-analysis.json')")
source=source.replace('print(json.dumps(data,indent=2))',"print(json.dumps({k:data[k] for k in ['run','verified_files','last_phase','configured_target_kill_observed','sa511_unsupported','enospc_lines','sceneboard_install_succeeded','sceneboard_process_observed','captures','mali_context_failure','desktop_verified']},indent=2))")
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
