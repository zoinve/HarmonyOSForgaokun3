"""Read the exact original proxy descriptor and encode a request with original Parcel APIs."""
from pathlib import Path
import runpy
import subprocess

parent=runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-identity-ipc-callback-012.py')))
source=parent['source']
sdk_source=parent['sdk_source']
anchor='    parcel_destroy(request);parcel_destroy(reply);stub_destroy(stub);'
assert sdk_source.count(anchor)==1
probe=r'''    void *samgr_proxy=dlopen("/sdk/libsamgr_proxy.z.so",RTLD_NOW|RTLD_LOCAL);
    check(samgr_proxy!=NULL,"load unchanged original SAMGR proxy");
    void *list_method=dlsym(samgr_proxy,"_ZN4OHOS25SystemAbilityManagerProxy19ListSystemAbilitiesEj");
    Dl_info proxy_info={0};
    check(list_method&&dladdr(list_method,&proxy_info)&&proxy_info.dli_fbase,
          "locate exact original proxy mapping");
    check((uintptr_t)list_method-(uintptr_t)proxy_info.dli_fbase==0x16c28,
          "exact audited proxy method offset");
    /* The audited LDP at 16d6c reads this exact-build descriptor view.
       This is read-only inspection, not a fabricated C++ object or service. */
    uint64_t descriptor_view[2];
    memcpy(descriptor_view,(const char *)proxy_info.dli_fbase+0x31b98,sizeof(descriptor_view));
    check(descriptor_view[0]>0&&descriptor_view[0]<128,
          "original descriptor view has bounded length");
    uintptr_t descriptor_address=(uintptr_t)descriptor_view[1];
    check(descriptor_address>=(uintptr_t)proxy_info.dli_fbase&&
          descriptor_address+2*(descriptor_view[0]+1)<=(uintptr_t)proxy_info.dli_fbase+0x30000,
          "descriptor string belongs to original proxy mapped image");
    const uint16_t *descriptor=(const uint16_t *)descriptor_address;
    char token[128]={0};
    for(size_t i=0;i<descriptor_view[0];++i) {
        check(descriptor[i]>=32&&descriptor[i]<127,"original descriptor is ASCII UTF16");
        token[i]=(char)descriptor[i];
    }
    check(descriptor[descriptor_view[0]]==0,"original descriptor is terminated");
    int (*write_token)(void *,const char *)=dlsym(capi,"OH_IPCParcel_WriteInterfaceToken");
    int (*write_i32)(void *,int32_t)=dlsym(capi,"OH_IPCParcel_WriteInt32");
    int (*data_size)(const void *)=dlsym(capi,"OH_IPCParcel_GetDataSize");
    const uint8_t *(*read_buffer)(const void *,int32_t)=dlsym(capi,"OH_IPCParcel_ReadBuffer");
    check(write_token&&write_i32&&data_size&&read_buffer,"resolve original public parcel codec APIs");
    void *encoded=parcel_create();
    check(encoded&&write_token(encoded,token)==0&&write_i32(encoded,15)==0,
          "original SDK encodes interface token and query flags");
    int encoded_size=data_size(encoded);
    check(encoded_size>0&&encoded_size<=512,"original encoded request is bounded");
    const uint8_t *encoded_data=read_buffer(encoded,encoded_size);
    check(encoded_data!=NULL,"original SDK exposes encoded request");
    printf("PARCEL041_REQUEST descriptor=%s code=5 argument=15 bytes=%d hex=",token,encoded_size);
    for(int i=0;i<encoded_size;++i) printf("%02x",encoded_data[i]);
    printf("\nPARCEL041_PASS original_proxy_descriptor=1 original_parcel_encoder=1 service_query_not_tested=1\n");
    parcel_destroy(encoded);
'''
sdk_source=sdk_source.replace(anchor,probe+anchor)
payload=parent['payload'];payload=payload[payload.index('\nfrom pathlib import Path')+1:]
payload='source='+repr(source)+'\nsdk_source='+repr(sdk_source)+'\n'+payload
payload=payload.replace('baremetal-identity-ipc-callback-012','baremetal-sdk-parcel-041')
anchor="pending=['libipc_common.z.so','libipc_capi.z.so']"
assert payload.count(anchor)==1
payload=payload.replace(anchor,"pending=['libipc_common.z.so','libipc_capi.z.so','libsamgr_proxy.z.so']")
# Guard the exact-build read-only descriptor offsets against the original audited DSO.
anchor="report=dict("
assert payload.count(anchor)==1
payload=payload.replace(anchor,"assert hashlib.sha256((work/'sdk/libsamgr_proxy.z.so').read_bytes()).hexdigest()=='9b916b2ac342e98da58aded0c71e8da9c98179d0e0ff3933d5a3506c4278d320'\n"+anchor)
compile(payload,'prepare-parcel-041','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=300)
    raise SystemExit(r.returncode)
