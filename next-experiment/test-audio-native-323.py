from pathlib import Path

BASE=Path(__file__).resolve().parent
if __name__=='__main__':
 source=(BASE/'test-audio-native-320.py').read_text().replace('audio-native-test-320.json','audio-native-test-323.json')
 anchor=' pthread_mutex_destroy(&render.lock);'
 extra=''' unsigned char s32[]={0,0,0xe8,3,0,0,0x18,0xfc};
 audio317_convert(output,s32,1,0.5f,AUDIO_VDI_CHANNEL_NORMAL,AUDIO_VDI_FORMAT_TYPE_PCM_32_BIT);
 assert(output[0]==0xf4 && output[1]==1 && output[2]==0x0c && output[3]==0xfe);
 attrs.format=AUDIO_VDI_FORMAT_TYPE_PCM_32_BIT;assert(audio317_attributes(&attrs));
'''
 assert source.count(anchor)==1
 source=source.replace(anchor,extra+anchor)
 exec(compile(source,'test-audio-native-323.generated.py','exec'),
      dict(__name__='__main__',__file__=str(BASE/'test-audio-native-323.generated.py')))
