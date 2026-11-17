from pathlib import Path
BASE=Path(__file__).resolve().parent
if __name__=='__main__':
    source=(BASE/'analyze-audio-389.py').read_text().replace('385','394')
    source=source.replace('audio-analysis-389.json','audio-analysis-398.json')
    anchor='   physical_jack_hotplug_verified=False,'
    assert source.count(anchor)==1
    source=source.replace(anchor,"   detector_config_observations=records(phase,'AUDIO393_CONFIG'),\n"+anchor)
    exec(compile(source,'analyze-audio-398.generated.py','exec'),
        dict(__name__='__main__',__file__=str(BASE/'analyze-audio-398.generated.py')))
