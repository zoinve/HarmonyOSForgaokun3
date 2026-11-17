"""New sample-accounting, route and public-renderer tests; no target execution."""
from pathlib import Path

BASE=Path(__file__).resolve().parent
if __name__=='__main__':
 # Reuse contract tests with new regressions and a distinct immutable report.
 original=(BASE/'test-audio-native-320.py').read_text()
 original=original.replace('audio-native-test-320.json','audio-native-test-352.json')
 anchor=' pthread_mutex_destroy(&render.lock);'
 extra=r''' struct AudioDeviceDescriptorVdi device={.pins=PIN_VDI_OUT_HEADPHONE};
 struct IAudioRenderVdi *created=(void *)(uintptr_t)1;
 assert(a_create_render(NULL,&device,&attrs,&created)==NOT_SUPPORTED&&!created);
 device.pins=PIN_VDI_OUT_SPEAKER;
 assert(a_create_render(NULL,&device,&attrs,&created)==OK&&created);
 assert(a_destroy_render(NULL,created)==OK);
 struct AudioRouteNodeVdi route_source={.role=AUDIO_VDI_PORT_SOURCE_ROLE,.type=AUDIO_VDI_PORT_MIX_TYPE};
 struct AudioRouteNodeVdi sink={.role=AUDIO_VDI_PORT_SINK_ROLE,.type=AUDIO_VDI_PORT_DEVICE_TYPE};
 sink.ext.device.type=PIN_VDI_OUT_SPEAKER;
 struct AudioRouteVdi route={.sources=&route_source,.sourcesLen=1,.sinks=&sink,.sinksLen=1};
 int32_t handle=-1;assert(a_route(NULL,&route,&handle)==OK&&handle==1);
 sink.ext.device.type=PIN_VDI_OUT_HEADPHONE;
 assert(a_route(NULL,&route,&handle)==NOT_SUPPORTED&&handle==-1);
 assert(a_route(NULL,NULL,&handle)==NOT_SUPPORTED&&handle==-1);
'''
 assert original.count(anchor)==1
 original=original.replace(anchor,extra+anchor)
 insertion="""  include=stage/'include';include.mkdir()
  sdk=BUILD/'sdk/native/sysroot/usr/include'
  for name in ['ohaudio','multimedia']:(include/name).symlink_to(sdk/name,target_is_directory=True)
  regression={}
  for name in ['idle-329','metrics-349','renderer-350']:
   program=stage/('test-'+name)
   subprocess.run(['gcc','-O1','-g','-Wall','-Wextra','-Werror','-ffunction-sections',
     '-fdata-sections','-Wl,--gc-sections','-fsanitize=address,undefined','-I',str(include),
     str(BASE/('test-audio-'+name+'.c')),'-ldl','-lm','-o',str(program)],check=True)
   regression[name]=subprocess.run([str(program)],capture_output=True,text=True,check=True,timeout=15).stdout
  subprocess.run([compiler,'-O2','-Wall','-Wextra','-Werror',str(BASE/'native-audio-renderer-350.c'),
     '-lohaudio','-lm','-o',str(stage/'renderer350')],check=True)
"""
 build_anchor="  subprocess.run(['aarch64-linux-gnu-gcc'"
 assert original.count(build_anchor)==1
 original=original.replace(build_anchor,insertion+build_anchor)
 original=original.replace('client_stdout=client.stdout,server_stdout=server.stdout,',
   'client_stdout=client.stdout,server_stdout=server.stdout,regression_stdout=regression,public_renderer_platform_built=True,')
 exec(compile(original,'test-audio-native-352.generated.py','exec'),
   dict(__name__='__main__',__file__=str(BASE/'test-audio-native-352.generated.py')))
