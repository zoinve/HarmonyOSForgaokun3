from pathlib import Path
import runpy

BASE=Path(__file__).resolve().parent
def vendor363():
 old=runpy.run_path(str(BASE/'native-audio-vdi-319.py'))
 source=old['vendor319']()
 for name in ['a_create_render','a_destroy_render','a_route','a_release_route','r_check_scene','r_select_scene']:
  source=old['replace_function'](source,name+'(','')
 anchor='static int32_t r_latency('
 assert source.count(anchor)==1
 return source.replace(anchor,'#include "native-audio-route-vdi-363.h"\n'+anchor,1)
