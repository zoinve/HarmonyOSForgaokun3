"""Separate real policy jack input from physical hotplug and acoustic acceptance."""
from pathlib import Path
BASE=Path(__file__).resolve().parent
if __name__=='__main__':
    source=(BASE/'analyze-audio-357.py').read_text()
    source=source.replace('commercial61-native-353','commercial61-native-385')
    source=source.replace('audio-analysis-357.json','audio-analysis-389.json')
    anchor='accepted_playback=metrics,total_accepted_frames=accepted,total_nonzero_frames=nonzero,'
    extra="""
   wire_version=2,ucm_routes=records(phase,'AUDIO363_ROUTE_READY'),jack_observations=records(phase,'AUDIO363_JACK'),
   original_policy_observations=records(phase,'AUDIO376_POLICY'),
   original_policy_jack_descriptors=records(phase,'AUDIO376_REAL_JACK_FD'),
   detector_input_results=records(phase,'AUDIO376_INPUT'),
   detector_initial_state_results=records(phase,'AUDIO376_STATE'),
   original_policy_real_jack_fd_verified=any(row.get('adapter_maps',0)>0 and row.get('real_jack_fds',0)>0
       and row.get('uid')==1041 for row in records(phase,'AUDIO376_POLICY')),
   original_policy_input_thread_alive=any(row.get('input_threads',0)>0 for row in records(phase,'AUDIO376_POLICY')),
   physical_jack_hotplug_verified=False,
"""
    assert source.count(anchor)==1;source=source.replace(anchor,anchor+extra)
    exec(compile(source,'analyze-audio-389.generated.py','exec'),
        dict(__name__='__main__',__file__=str(BASE/'analyze-audio-389.generated.py')))
