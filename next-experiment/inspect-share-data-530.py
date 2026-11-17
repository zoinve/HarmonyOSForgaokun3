"""Read only bounded, redacted P2P counters after the user's517 restart."""
from pathlib import Path
import linecache

BASE=Path(__file__).resolve().parent
if __name__ == '__main__':
    source=(BASE/'inspect-share-data-512.py').read_text()
    source=source.replace('commercial61-native-502','commercial61-native-517')
    source=source.replace('boot-observation-506.json','boot-observation-522.json')
    source=source.replace('share-data-analysis-512.json','share-data-analysis-530.json')
    source=source.replace('harmony-share-lab-512','harmony-share-lab-530')
    source=source.replace('harmony-share-data-512','harmony-share-data-530')
    anchor="if __name__ == '__main__':"
    assert source.count(anchor)==1
    patterns=dict(config_parse_failure=r'Line \d+:.*(?:failed|unknown|Invalid)',
                  interface_initialization_failure=r'Failed to initialize interface',
                  initialized_banner=r'Successfully initialized wpa_supplicant',
                  device_creation_failure=r'Failed to create.*interface|Failed to create P2P',
                  no_supported_channels=r'No supported channels|No common channels',
                  terminating=r'CTRL-EVENT-TERMINATING',
                  p2p_find_stopped=r'P2P-FIND-STOPPED',
                  negotiation_failure=r'P2P-GO-NEG-FAILURE',
                  negotiation_success=r'P2P-GO-NEG-SUCCESS')
    source=source.replace(anchor,'PATTERNS.update('+repr(patterns)+')\n\n'+anchor,1)
    filename=str(BASE/'inspect-share-data-530.generated.py')
    linecache.cache[filename]=(len(source),None,source.splitlines(keepends=True),filename)
    exec(compile(source,filename,'exec'),dict(__name__='__main__',__file__=filename))
