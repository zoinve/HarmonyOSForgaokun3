from pathlib import Path

source = Path(__file__).with_name('analyze-commercial-hwbreak-050.py').read_text()
source = source.replace('commercial61-native-050', 'commercial61-native-051').replace('COMMERCIAL050', 'COMMERCIAL051')
source = source.replace('ATTACH_FAILED|MMAP_FAILED|ENABLE_FAILED|MAPPING_WAIT', 'ATTACH_FAILED|MMAP_FAILED|ENABLE_FAILED|MAP_FILE_REJECTED|MAPPING_WAIT')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
