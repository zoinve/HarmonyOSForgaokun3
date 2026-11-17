"""420 playback regression plus actual capture/worker metadata, not acoustics."""
from pathlib import Path
BASE=Path(__file__).resolve().parent
if __name__=='__main__':
    source=(BASE/'analyze-audio-357.py').read_text()
    source=source.replace('commercial61-native-353','commercial61-native-420')
    source=source.replace('audio-analysis-357.json','audio-analysis-425.json')
    anchor='accepted_playback=metrics,total_accepted_frames=accepted,total_nonzero_frames=nonzero,'
    extra="""
   wire_version=2,ucm_routes=records(phase,'AUDIO363_ROUTE_READY'),jack_observations=records(phase,'AUDIO363_JACK'),
   original_policy_observations=records(phase,'AUDIO376_POLICY'),
   original_policy_jack_descriptors=records(phase,'AUDIO376_REAL_JACK_FD'),
   detector_input_results=records(phase,'AUDIO376_INPUT'),
   detector_initial_state_results=records(phase,'AUDIO376_STATE'),
   detector_config_observations=records(phase,'AUDIO393_CONFIG'),
   original_policy_real_jack_fd_verified=any(row.get('adapter_maps',0)>0 and row.get('real_jack_fds',0)>0
       and row.get('uid')==1041 for row in records(phase,'AUDIO376_POLICY')),
   original_policy_input_thread_alive=any(row.get('input_threads',0)>0 for row in records(phase,'AUDIO376_POLICY')),
   physical_jack_hotplug_verified=False,
   duplex_listener=records(phase,'AUDIO411_LISTEN'),
   card_leases=records(phase,'AUDIO410_LEASE'),
   capture_ready=records(phase,'AUDIO411_CAPTURE_READY'),
   capture_io=records(phase,'AUDIO411_CAPTURE_IO'),
   capture_ends=records(phase,'AUDIO411_CAPTURE_END'),
   worker_shutdown=records(phase,'AUDIO411_SHUTDOWN'),
   microphone_hardware_acceptance=False,
"""
    assert source.count(anchor)==1
    source=source.replace(anchor,anchor+extra)
    source=source.replace('microphone_recorded=False',
        "microphone_recorded=any(row.get('actual_frames',0)>0 for row in records(phase,'AUDIO411_CAPTURE_END'))")
    exec(compile(source,'analyze-audio-425.generated.py','exec'),
         dict(__name__='__main__',__file__=str(BASE/'analyze-audio-425.generated.py')))
