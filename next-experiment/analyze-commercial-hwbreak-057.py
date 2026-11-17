from pathlib import Path

source = Path(__file__).with_name('analyze-commercial-hwbreak-050.py').read_text()
source = source.replace('commercial61-native-050', 'commercial61-native-057').replace('COMMERCIAL050', 'COMMERCIAL057')
source = source.replace('ATTACH_FAILED|MMAP_FAILED|ENABLE_FAILED|MAPPING_WAIT', 'ATTACH_FAILED|MMAP_FAILED|ENABLE_FAILED|MEMORY_REJECTED|MAPPING_CHANGED|MAPPING_WAIT')
source = source.replace("['ip'] + ['x' + str(i) for i in range(7)]", "['ip'] + ['x' + str(i) for i in range(7)] + ['x9']")
source = source.replace('x6=0x6\'', 'x6=0x6 x9=0x9\'')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
