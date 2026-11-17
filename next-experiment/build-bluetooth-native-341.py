"""Request the original Bluetooth Settings ability; observe real HCI discovery."""
from pathlib import Path
import runpy

BASE=Path(__file__).resolve().parent
AUDIO=runpy.run_path(str(BASE/'build-audio-native-321.py'))
ONCE=AUDIO['ONCE']

def outer341(source,old_digest,digest):
 source=AUDIO['outer321'](source,old_digest,digest)
 source=source.replace('/commercial61-native-321/bootstrap-runtime087','/commercial61-native-341/bootstrap-runtime087')
 source=ONCE(source,'static void native_original(void)\n{',
   (BASE/'native-bluetooth-ui-339.h').read_text()+'\nstatic void native_original(void)\n{')
 return ONCE(source,'                if(i==4||i==7)audio321_observe(child);',
   '                if(i==4||i==7)audio321_observe(child);\n                if(i==7)bt339_start(child);')

def extra341(compile_program,stage,entries):
 AUDIO['extra321'](compile_program,stage,entries)
 broker=(BASE/'native-qca-broker-022.c').read_text()
 broker=ONCE(broker,'struct hci_address {',
   '#include "native-bt-discovery-340.h"\nstruct hci_address {')
 broker=ONCE(broker,'                if(send(hci,queued,',
   '                bt340_command(queued,(size_t)size);\n                if(send(hci,queued,')
 broker=ONCE(broker,'            if(write_all(client,packet,',
   '            bt340_event(packet,(size_t)n);\n            if(write_all(client,packet,')
 compile_program('qca-broker340',broker)
 entries['radio261/qca-broker']=(0o100755,(stage/'qca-broker340').read_bytes())

if __name__=='__main__':
 runpy.run_path(str(BASE/'driver-builder-305.py'))['build'](
   341,AUDIO['runtime321'],outer341,AUDIO['RADIO']['vendor297'],extra341)
