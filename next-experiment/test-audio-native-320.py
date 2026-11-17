from pathlib import Path
import json
import runpy
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'next-experiment'
BUILD=Path('/home/zoinve/harmony-virgl-883')
HEADERS=BUILD/'audio-contract-314-peripheral/audio/interfaces/sound/v1_0'
HARNESS=r'''
#include "vendor.c"
#include <assert.h>
#include <stdio.h>
int main(void) {
 assert(access(AUDIO315_SOCKET,F_OK)!=0);
 struct AudioSampleAttributesVdi attrs={.sampleRate=48000,.channelCount=2,.format=AUDIO_VDI_FORMAT_TYPE_PCM_16_BIT};
 struct NativeRender render;init_render(&render,&attrs);
 assert(r_start(&render.api)!=OK && !render.started);
 int8_t data[16]={0};uint64_t done=123;
 assert(r_frame(&render.api,data,sizeof(data),&done)!=OK && done==0);
 assert(r_set_volume(&render.api,2.0f)==ERR);
 assert(r_set_gain(&render.api,-1.0f)==ERR);
 assert(r_set_speed(&render.api,2.0f)==NOT_SUPPORTED);
 struct NativeCapture capture;init_capture(&capture,&attrs);
 assert(c_start(&capture.api)==NOT_SUPPORTED);
 uint32_t length=sizeof(data);done=123;
 assert(c_frame(&capture.api,data,&length,&done)==NOT_SUPPORTED && !done && !length);
 unsigned char input[]={0xe8,3,0x18,0xfc},output[4];
 audio317_scale(output,input,4,0.5f,AUDIO_VDI_CHANNEL_NORMAL);
 assert(output[0]==0xf4 && output[1]==1 && output[2]==0x0c && output[3]==0xfe);
 audio317_scale(output,input,4,1.0f,AUDIO_VDI_CHANNEL_BOTH_MUTE);
 assert(!output[0]&&!output[1]&&!output[2]&&!output[3]);
 struct audio315_reply reply={.magic=AUDIO315_MAGIC,.version=AUDIO315_VERSION,.rate=48000,.channels=2,.frame_bytes=4,.period_frames=1,.buffer_frames=4,.monotonic_ns=1,.submitted_frames=4,.played_frames=2,.delay_frames=2};
 assert(audio317_valid(&reply,0));reply.played_frames=3;assert(!audio317_valid(&reply,0));
 pthread_mutex_destroy(&render.lock);
 puts("AUDIO320_CLIENT passed=1 missing_backend_is_error=1 microphone_samples_faked=0 hardware_acceptance=0");
 return 0;
}
'''

if __name__=='__main__':
 output=ROOT/'reports/audio-native-test-320.json'
 assert not output.exists()
 source=runpy.run_path(str(BASE/'native-audio-vdi-319.py'))['vendor319']()
 with tempfile.TemporaryDirectory(prefix='audio320-') as directory:
  stage=Path(directory);(stage/'vendor.c').open('x').write(source)
  (stage/'test.c').open('x').write(HARNESS)
  includes=['-I',str(BASE),'-I',str(HEADERS)]
  compiler=str(BUILD/'window-bridge/toolchain/ohos-cc')
  subprocess.run([compiler,'-O2','-Wall','-Wextra','-Werror','-shared','-fPIC',
    '-Wl,--no-undefined,-soname,libaudio_primary_impl.z.so',*includes,
    str(stage/'vendor.c'),'-o',str(stage/'libaudio_primary_impl.z.so')],check=True)
  subprocess.run(['gcc','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
    *includes,str(stage/'test.c'),'-pthread','-lm','-o',str(stage/'test')],check=True)
  client=subprocess.run([str(stage/'test')],capture_output=True,text=True,check=True)
  subprocess.run(['gcc','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
    str(BASE/'test-audio-server-318.c'),'-ldl','-o',str(stage/'server-test')],check=True)
  server=subprocess.run([str(stage/'server-test')],capture_output=True,text=True,check=True)
  subprocess.run(['aarch64-linux-gnu-gcc','-O2','-Wall','-Wextra','-Werror',
    str(BASE/'native-audio-server-316.c'),'-ldl','-o',str(stage/'server')],check=True)
 commit=subprocess.check_output(['git','-C',str(HEADERS.parents[3]),'rev-parse','HEAD'],text=True).strip()
 result=dict(official_vdi_headers_commit=commit,platform_library_built=True,
  arm64_server_built=True,address_and_undefined_sanitizers_passed=True,
  client_stdout=client.stdout,server_stdout=server.stdout,
  hardware_playback_verified=False,original_service_tested=False,source_images_modified=False)
 output.open('x').write(json.dumps(result,indent=2))
 print(json.dumps(result,indent=2))
