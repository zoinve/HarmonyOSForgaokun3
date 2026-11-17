"""Bounded own-driver request logging and public original-service metadata."""
LOGGER = r'''
#ifndef COMMERCIAL073_TRACE_PATH
#define COMMERCIAL073_TRACE_PATH "/data/native-allocator-073.trace"
#endif
static void allocator073_request(const BufferAllocInfo &info)
{
    const int saved073 = errno;
    static std::atomic<unsigned> count073{0};
    unsigned sequence073 = count073.fetch_add(1, std::memory_order_relaxed);
    if (sequence073 < 128) {
        int fd073 = open(COMMERCIAL073_TRACE_PATH,
            O_WRONLY | O_APPEND | O_CLOEXEC | O_NOFOLLOW);
        if (fd073 >= 0) {
            dprintf(fd073, "COMMERCIAL073_ALLOC_REQUEST sequence=%u pid=%ld uid=%u width=%u height=%u format=%d usage=0x%llx expected=%llu public_interface=1\n",
                sequence073, static_cast<long>(getpid()), static_cast<unsigned>(getuid()),
                info.width, info.height, static_cast<int>(info.format),
                static_cast<unsigned long long>(info.usage),
                static_cast<unsigned long long>(info.expectedSize));
            close(fd073);
        }
    }
    errno = saved073;
}
'''


def allocator(source):
    assert 'COMMERCIAL073_ALLOC_REQUEST' not in source
    assert source.count('#include <cerrno>') == 1
    source = source.replace('#include <cerrno>', '#include <cerrno>\n#include <atomic>', 1)
    anchor = 'bool supported(uint32_t width, uint32_t height, uint32_t format, uint64_t usage)'
    assert source.count(anchor) == 1
    source = source.replace(anchor, LOGGER + '\n' + anchor, 1)
    anchor = '        out = nullptr;'
    assert source.count(anchor) == 1
    return source.replace(anchor, anchor + '\n        allocator073_request(info);', 1)


INVENTORY = r'''
static void commercial_allocator_inventory073(unsigned sample)
{
 if(sample!=8 && sample!=12 && sample!=18 && sample!=28)return;
 const int saved073=errno;
 commercial_stream043("/data/native-allocator-073.trace",sample,0,65536);
 const char *logs073[]={"/data/local/tmp/l410-kylin-h264-decoder.log","/data/local/tmp/l410-kylin-video-decoder.log"};
 for(unsigned i073=0;i073<2;++i073)commercial_stream043(logs073[i073],sample,0,32768);
 DIR *directory073=opendir("/proc");
 struct dirent *entry073;
 if(!directory073){errno=saved073;return;}
 while((entry073=readdir(directory073))){
  char *end073;long pid073=strtol(entry073->d_name,&end073,10);
  if(!*entry073->d_name || *end073 || pid073<=0)continue;
  char path073[256],comm073[64],command073[4096],status073[8192];
  snprintf(path073,sizeof(path073),"/proc/%ld/comm",pid073);
  if(read_path(path073,comm073,sizeof(comm073))<=0)continue;
  comm073[strcspn(comm073,"\n")]=0;
  snprintf(path073,sizeof(path073),"/proc/%ld/cmdline",pid073);
  ssize_t size073=read_path(path073,command073,sizeof(command073));
  if(size073<=0)continue;
  for(ssize_t i073=0;i073<size073;++i073)if(!command073[i073])command073[i073]=' ';
  const char *role073=NULL;unsigned wanted073=0;
  if(!strcmp(comm073,"allocator_host")){role073="allocator_host";wanted073=3041;}
  else if(!strncmp(comm073,"av_codec_servic",15)){role073="av_codec_service";wanted073=1013;}
  else if(strstr(command073,"/system/lib64/commercial-software-codec072/ld-linux-aarch64.so.1") &&
          strstr(command073,"/system/lib64/commercial-software-codec072/helper"))role073="software_helper";
  if(!role073)continue;
  snprintf(path073,sizeof(path073),"/proc/%ld/status",pid073);
  if(read_path(path073,status073,sizeof(status073))<=0)continue;
  char *uids073=strstr(status073,"\nUid:");unsigned real073,effective073,saveduid073,fs073;
  if(!uids073 || sscanf(uids073,"\nUid: %u %u %u %u",&real073,&effective073,&saveduid073,&fs073)!=4 ||
     real073!=wanted073 || effective073!=wanted073 || saveduid073!=wanted073 || fs073!=wanted073)continue;
  char executable073[512];
  snprintf(path073,sizeof(path073),"/proc/%ld/exe",pid073);
  ssize_t length073=readlink(path073,executable073,sizeof(executable073)-1);
  if(length073<=0)continue;
  executable073[length073]=0;
  dprintf(commercial_diag_fd003,"COMMERCIAL073_PUBLIC_SERVICE sample=%u pid=%ld role=%s uid=%u exe=%s command=%s\n",
    sample,pid073,role073,wanted073,executable073,command073);
  snprintf(path073,sizeof(path073),"/proc/%ld/status",pid073);
  commercial_stream043(path073,sample,(unsigned)pid073,16384);
  snprintf(path073,sizeof(path073),"/proc/%ld/maps",pid073);
  commercial_stream043(path073,sample,(unsigned)pid073,262144);
  if(strcmp(role073,"allocator_host")){
   for(unsigned i073=0;i073<2;++i073){
    snprintf(path073,sizeof(path073),"/proc/%ld/root%s",pid073,logs073[i073]);
    commercial_stream043(path073,sample,(unsigned)pid073,32768);
   }
  }
 }
 closedir(directory073);errno=saved073;
}
'''


def inner(source):
    assert 'static void commercial_allocator_inventory073(' not in source
    anchor = '    commercial_copy005("/graphics016/vendor/lib64/libdisplay_buffer_vdi_impl.z.so","/run/commercial-vendor004/upper/lib64/libdisplay_buffer_vdi_impl.z.so",420);'
    assert source.count(anchor) == 1
    source = source.replace(anchor, anchor.replace('/graphics016/vendor/lib64/libdisplay_buffer_vdi_impl.z.so', '/allocator073/libdisplay_buffer_vdi_impl.z.so'), 1)
    anchor = '    dprintf(1,"COMMERCIAL016_GRAPHICS original_service_credentials_unchanged=1 own_hardware_backends=1 sdk_payload=0 original_cursor_adapter=1\\n");'
    assert source.count(anchor) == 1
    extra = r'''
    int fd073=open("/data/native-allocator-073.trace",O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0640);
    if(fd073<0 || fchown(fd073,3041,1003) || fchmod(fd073,0640) || close(fd073))fail("original allocator trace writer");
'''
    source = source.replace(anchor, extra + '\n' + anchor, 1)
    anchor = 'static void commercial_observer(void)'
    assert source.count(anchor) == 1
    source = source.replace(anchor, INVENTORY + '\n' + anchor, 1)
    anchor = '        commercial_capture016(sample);'
    assert source.count(anchor) == 1
    return source.replace(anchor, anchor + '\n        commercial_allocator_inventory073(sample);', 1)
