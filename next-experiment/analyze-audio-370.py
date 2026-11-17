from pathlib import Path
BASE=Path(__file__).resolve().parent
if __name__=='__main__':
 source=(BASE/'analyze-audio-357.py').read_text()
 source=source.replace('commercial61-native-353','commercial61-native-365')
 source=source.replace('audio-analysis-357.json','audio-analysis-370.json')
 anchor='accepted_playback=metrics,total_accepted_frames=accepted,total_nonzero_frames=nonzero,'
 assert source.count(anchor)==1
 source=source.replace(anchor,anchor+"\n   wire_version=2,ucm_routes=records(phase,'AUDIO363_ROUTE_READY'),jack_observations=records(phase,'AUDIO363_JACK'),")
 exec(compile(source,'analyze-audio-370.generated.py','exec'),
   dict(__name__='__main__',__file__=str(BASE/'analyze-audio-370.generated.py')))
