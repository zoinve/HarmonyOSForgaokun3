from pathlib import Path
BASE=Path(__file__).resolve().parent
if __name__=='__main__':
 source=(BASE/'test-audio-native-320.py').read_text()
 source=source.replace('audio-native-test-320.json','audio-native-test-364.json')
 source=source.replace('native-audio-vdi-319.py','native-audio-vdi-363.py').replace("['vendor319']()","['vendor363']()")
 anchor=' pthread_mutex_destroy(&render.lock);'
 extra=r''' struct AudioDeviceDescriptorVdi device={.pins=PIN_VDI_OUT_HEADPHONE};
 struct IAudioRenderVdi *created=NULL,*other=(void *)(uintptr_t)1;
 assert(a_create_render(NULL,&device,&attrs,&created)==OK&&created);
 assert(((struct NativeRender *)created)->route==AUDIO363_HEADPHONES);
 assert(a_create_render(NULL,&device,&attrs,&other)==ERR&&!other);
 assert(r_start(created)!=OK&&!((struct NativeRender *)created)->started);
 assert(((struct NativeRender *)created)->route==AUDIO363_HEADPHONES);
 assert(a_destroy_render(NULL,created)==OK);
 device.pins=PIN_VDI_OUT_USB;
 assert(a_create_render(NULL,&device,&attrs,&created)==NOT_SUPPORTED&&!created);
 struct AudioSceneDescriptorVdi scene={.desc={.pins=PIN_VDI_OUT_HEADPHONE}};
 assert(r_select_scene(&render.api,&scene)!=OK&&render.route==AUDIO363_HEADPHONES&&!render.started);
 assert(r_start(&render.api)!=OK&&render.route==AUDIO363_HEADPHONES);
 reply.route=2;assert(!audio317_valid(&reply,0));
 assert(a_release_route(NULL,9)==ERR);
'''
 assert source.count(anchor)==1;source=source.replace(anchor,extra+anchor)
 anchor="  subprocess.run(['aarch64-linux-gnu-gcc'"
 extra="""  regressions={}
  for name in ['server-routes-363','idle-329','metrics-349']:
   program=stage/name
   subprocess.run(['gcc','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
     str(BASE/('test-audio-'+name+'.c')),'-ldl','-o',str(program)],check=True)
   regressions[name]=subprocess.run([str(program)],capture_output=True,text=True,check=True,timeout=15).stdout
"""
 assert source.count(anchor)==1;source=source.replace(anchor,extra+anchor)
 source=source.replace('client_stdout=client.stdout,server_stdout=server.stdout,',
   'client_stdout=client.stdout,server_stdout=server.stdout,route_regressions=regressions,wire_version=2,')
 exec(compile(source,'test-audio-native-364.generated.py','exec'),
   dict(__name__='__main__',__file__=str(BASE/'test-audio-native-364.generated.py')))
