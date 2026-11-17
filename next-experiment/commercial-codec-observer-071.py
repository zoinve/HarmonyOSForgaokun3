"""Original codec return registers and public proc metadata only."""
from pathlib import Path
import hashlib
import json
import struct

BASE=Path(__file__).resolve().parents[1]
POINTS=[
    ('avcodec_open_result','libfcodec.z.so',0x15d5c,'0bc475ded266f428b0c40633f85dd1347de2aa208876b142c414b0499f5c9527'),
    ('hevc_create_result','libhevc_decoder.z.so',0x16750,'760e6f2ea82bc1a7970bdb63dd56c2be1d556ae8a435777e50325b47dc8b714a'),
    ('hevc_params_result','libhevcdec_ohos.z.so',0x498e4,'63afbe44aa6826abec38396f2ed18db101ebb9704443387ce1e9795e21e3fef7'),
    ('hevc_alloc_result','libhevcdec_ohos.z.so',0x49920,'63afbe44aa6826abec38396f2ed18db101ebb9704443387ce1e9795e21e3fef7'),
]


def specifications():
    result=[]
    for name,library,address,expected in POINTS:
        data=(BASE/'reports/commercial-decoder-audit-070'/library).read_bytes()
        assert hashlib.sha256(data).hexdigest()==expected
        assert data[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',data,18)[0]==183
        start=struct.unpack_from('<Q',data,32)[0]
        size,count=struct.unpack_from('<HH',data,54)
        matches=[]
        for index in range(count):
            kind,flags,offset,virtual,_,length,_,_=struct.unpack_from('<IIQQQQQQ',data,start+index*size)
            if kind==1 and flags&1 and virtual<=address and address+4<=virtual+length:
                matches.append(offset+address-virtual)
        assert len(matches)==1 and address%4==0
        offset=matches[0]
        result.append(dict(event=name,library=library,virtual_address=hex(address),file_offset=hex(offset),
            instruction=int.from_bytes(data[offset:offset+4],'little'),sha256=expected))
    return result


FIND = r'''
static pid_t hw071_find_service(pid_t child)
{
 char path[128],expected[128],actual[128],command[4096],comm[64],status[8192];
 snprintf(path,sizeof(path),"/proc/%d/ns/pid",child);
 ssize_t n=readlink(path,expected,sizeof(expected)-1);if(n<=0)return 0;expected[n]=0;
 DIR *dir=opendir("/proc");if(!dir)return 0;struct dirent *entry;pid_t service=0;
 while((entry=readdir(dir))){
  char *end;long pid=strtol(entry->d_name,&end,10);
  if(!*entry->d_name || *end || pid<=0)continue;
  snprintf(path,sizeof(path),"/proc/%ld/comm",pid);
  if(read_text(path,comm,sizeof(comm)) || strncmp(comm,"av_codec_servic",15))continue;
  snprintf(path,sizeof(path),"/proc/%ld/cmdline",pid);
  if(read_text(path,command,sizeof(command)))continue;
  snprintf(path,sizeof(path),"/proc/%ld/status",pid);
  if(read_text(path,status,sizeof(status)))continue;
  char *uidline=strstr(status,"\nUid:");unsigned realuid,effectiveuid,saveduid,fsuid;
  if(!uidline || sscanf(uidline,"\nUid: %u %u %u %u",&realuid,&effectiveuid,&saveduid,&fsuid)!=4 ||
     realuid!=1013 || effectiveuid!=1013 || saveduid!=1013 || fsuid!=1013)continue;
  snprintf(path,sizeof(path),"/proc/%ld/ns/pid",pid);
  n=readlink(path,actual,sizeof(actual)-1);if(n<=0)continue;actual[n]=0;
  if(!strcmp(expected,actual)){service=(pid_t)pid;break;}
 }
 closedir(dir);return service;
}
'''

TICK = r'''
static void hw071_tick(pid_t child,int final)
{
 int saved=errno;
 if(final){
  for(unsigned i=0;i<HW071_SLOTS;++i)if(hw071_events[i].used)hw071_close(&hw071_events[i]);
  dprintf(1,"COMMERCIAL071_CODEC_HW_STOPPED original_service_unmodified=1\n");errno=saved;return;
 }
 pid_t service=hw071_find_service(child);
 if(service!=hw071_service){
  for(unsigned i=0;i<HW071_SLOTS;++i)if(hw071_events[i].used)hw071_close(&hw071_events[i]);
  memset(hw071_addresses,0,sizeof(hw071_addresses));hw071_service=service;
  if(service)dprintf(1,"COMMERCIAL071_CODEC_HW_SETUP_BEGIN global_pid=%d child=%d\n",service,child);
 }
 if(service){
  if(hw071_resolve(service)){
   dprintf(1,"COMMERCIAL071_CODEC_HW_RESOLVE_REFUSED global_pid=%d errno=%d\n",service,errno);
   errno=saved;return;
  }
  for(unsigned i=0;i<HW071_SLOTS;++i)if(hw071_events[i].used){
   char path[128];snprintf(path,sizeof(path),"/proc/%d/task/%d",service,hw071_events[i].tid);
   if(access(path,F_OK))hw071_close(&hw071_events[i]);
  }
  hw071_attach(service);
 }else dprintf(1,"COMMERCIAL071_CODEC_HW_WAIT_SERVICE child=%d\n",child);
 for(unsigned i=0;i<HW071_SLOTS;++i)if(hw071_events[i].used)hw071_drain(&hw071_events[i]);
 errno=saved;
}
'''


def helper():
    source=(BASE/'next-experiment/commercial-hwbreak-050.h').read_text()
    source=source.replace('hw050','hw071').replace('HW050','HW071').replace('COMMERCIAL050_HW','COMMERCIAL071_CODEC_HW')
    specs=['{'+','.join([json.dumps(r['event']),json.dumps(r['library']),r['file_offset']+'ULL',hex(r['instruction'])+'u'])+'}' for r in specifications()]
    source=source.replace('HW071_SPECS',',\n'.join(specs))
    start=source.index('static pid_t hw071_find_service(')
    end=source.index('static int hw071_resolve(',start)
    source=source[:start]+FIND+'\n'+source[end:]
    source=source[:source.index('static void hw071_tick(')]+TICK
    anchor='        const struct hw071_spec *spec=&hw071_specs[i];'
    assert source.count(anchor)==1
    source=source.replace(anchor,'        if(hw071_addresses[i])continue;\n'+anchor,1)
    source=source.replace('fclose(maps);if(!address){errno=EAGAIN;return -1;}',
                          'fclose(maps);if(!address)continue;',1)
    anchor='        for(unsigned spec=0;spec<HW071_EVENTS;++spec){'
    assert source.count(anchor)==1
    source=source.replace(anchor,anchor+'\n            if(!hw071_addresses[spec])continue;',1)
    return source


def outer(source):
    anchor='static void native_original(void)'
    assert source.count(anchor)==1
    source=source.replace(anchor,helper()+'\n'+anchor,1)
    assert source.count('hw050_tick(child,0);')==2
    source=source.replace('hw050_tick(child,0);','hw050_tick(child,0);hw071_tick(child,0);')
    assert source.count('hw050_tick(child,1);')==1
    return source.replace('hw050_tick(child,1);','hw050_tick(child,1);hw071_tick(child,1);',1)


INNER = r'''
static void codec071_inventory(unsigned sample,long pid)
{
 if(sample<8 || sample>28 || sample%2)return;
 const int saved=errno;char path[256],comm[64],status[8192];
 snprintf(path,sizeof(path),"/proc/%ld/comm",pid);
 if(read_path(path,comm,sizeof(comm))<=0 || strncmp(comm,"av_codec_servic",15)){errno=saved;return;}
 snprintf(path,sizeof(path),"/proc/%ld/status",pid);
 if(read_path(path,status,sizeof(status))<=0){errno=saved;return;}
 char *uidline=strstr(status,"\nUid:");unsigned realuid,effectiveuid,saveduid,fsuid;
 if(!uidline || sscanf(uidline,"\nUid: %u %u %u %u",&realuid,&effectiveuid,&saveduid,&fsuid)!=4 ||
    realuid!=1013 || effectiveuid!=1013 || saveduid!=1013 || fsuid!=1013){errno=saved;return;}
 dprintf(commercial_diag_fd003,"COMMERCIAL071_CODEC_INVENTORY sample=%u pid=%ld original_uid=%u\n",sample,pid,effectiveuid);
 snprintf(path,sizeof(path),"/proc/%ld/maps",pid);commercial_stream043(path,sample,pid,1048576);
 snprintf(path,sizeof(path),"/proc/%ld/status",pid);commercial_stream043(path,sample,pid,65536);
 errno=saved;
}
'''


def inner(source):
    anchor='static void commercial_observer(void)'
    assert source.count(anchor)==1
    source=source.replace(anchor,INNER+'\n'+anchor,1)
    anchor='            if(!strcmp(text,"com.huawei.hmos.hwstartupguide"))commercial_resource_inventory069(sample,id);'
    assert source.count(anchor)==1
    return source.replace(anchor,'            codec071_inventory(sample,id);\n'+anchor,1)
