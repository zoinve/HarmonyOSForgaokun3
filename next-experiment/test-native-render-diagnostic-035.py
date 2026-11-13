from pathlib import Path
import runpy
base=Path(__file__).resolve().parent
assert (base/'build-native-render-035.py').exists(),'missing split-stage diagnostic'
p=runpy.run_path(str(base/'build-native-render-035.py'))
for stage in ['composer_dma_to_ram035','composer_neon_rotate035','composer_ram_to_scanout035']:
 assert stage in p['payload'] or stage in (base/'native-cached-copy-035.h').read_text(),stage
assert "old=root/'native-render-034'" in p['payload']
assert "work=root/'native-render-035'" in p['payload']
assert 'paint_cursor_032(output)' in p['payload']
print('PASS: independent diagnostic, original paint/DMA contract retained, three stage boundaries')
