"""Original SDK Parcel/SendRequest against a real kernel, only in guarded QEMU."""
from pathlib import Path
import runpy
import subprocess

base=Path(__file__).resolve().parent
parent=runpy.run_path(str(base/'prepare-baremetal-identity-native-read-009.py'))
source=parent['source'].replace('IDENTITY009_','IDENTITY010_')
# Keep the existing mapping: Binder permits only one mmap per open file.
anchor='    munmap(mapping,1024*1024);'
assert source.count(anchor)==1
source=source.replace(anchor,'    /* Mapping retained for the original SDK transaction below. */')
anchor='    require(child_status(sdk_child),'
assert source.count(anchor)==1
server=r'''    struct binder_reader_003 sdk_reader={.fd=binder};
    struct binder_transaction_data sdk_request=binder_next_003(&sdk_reader,BR_TRANSACTION);
    printf("IPC010_SERVER code=%u uid=%u bytes=%llu\n",sdk_request.code,sdk_request.sender_euid,
           (unsigned long long)sdk_request.data_size);
    require(sdk_request.code==0x510&&sdk_request.sender_euid==0&&sdk_request.data_size==8,
            "original SDK transaction code, UID and parcel size");
    require(*(uint64_t *)(uintptr_t)sdk_request.data.ptr.buffer==0xabc010,
            "original SDK Parcel payload reaches actual kernel receiver");
    binder_identity_003(binder,0x5000000000000500ULL,0x6000000000000600ULL,sdk_child);
    uint64_t sdk_response=0xdef010;
    struct binder_transaction_data sdk_reply={.data_size=sizeof(sdk_response),
        .data.ptr.buffer=(uintptr_t)&sdk_response};
    binder_write_003(binder,BC_REPLY,&sdk_reply,sizeof(sdk_reply));
    binder_write_003(binder,BC_FREE_BUFFER,&sdk_request.data.ptr.buffer,sizeof(binder_uintptr_t));
    munmap(manager_mapping,1024*1024);
'''
source=source.replace(anchor,server+anchor)
sdk_source=parent['sdk_source'].replace('SDK009_','SDK010_').replace('IPC009_','IPC010_')
anchor='    printf("SDK010_PASS checks='
assert sdk_source.count(anchor)==1
client=r'''    void *capi=dlopen("libipc_capi.z.so",RTLD_NOW|RTLD_LOCAL);
    if(!capi)fprintf(stderr,"IPC010_CAPI_DLOPEN %s\n",dlerror());
    check(capi!=NULL,"load unmodified original SDK Parcel and BinderInvoker closure");
    void *(*parcel_create)(void)=dlsym(capi,"OH_IPCParcel_Create");
    void (*parcel_destroy)(void *)=dlsym(capi,"OH_IPCParcel_Destroy");
    int (*parcel_write)(void *,uint64_t)=dlsym(capi,"OH_IPCParcel_WriteUint64");
    int (*parcel_read)(const void *,uint64_t *)=dlsym(capi,"OH_IPCParcel_ReadUint64");
    void *(*invoker_get)(int)=dlsym(capi,"_ZN4OHOS17IPCThreadSkeleton16GetRemoteInvokerEi");
    void (*option_init)(void *,int,int)=dlsym(capi,"_ZN4OHOS13MessageOptionC1Eii");
    int (*send_request)(void *,int,uint32_t,void *,void *,void *)=
        dlsym(capi,"_ZN4OHOS13BinderInvoker11SendRequestEijRNS_13MessageParcelES2_RNS_13MessageOptionE");
    check(parcel_create&&parcel_destroy&&parcel_write&&parcel_read&&invoker_get&&option_init&&send_request,
          "resolve original SDK allocation, parcel and transaction methods");
    void *invoker=invoker_get(0),*request=parcel_create(),*reply=parcel_create();
    check(invoker&&request&&reply,"original SDK constructs Binder invoker and parcels");
    check(parcel_write(request,0xabc010)==0,"original SDK writes request parcel");
    /* Test adapter for the exact hashed SDK DSO: its C wrapper holds one pointer.
       Verified from Create/WriteUint64 disassembly; no C++ object allocation here. */
    void *request_cpp=NULL,*reply_cpp=NULL;
    memcpy(&request_cpp,request,sizeof(request_cpp));memcpy(&reply_cpp,reply,sizeof(reply_cpp));
    check(request_cpp&&reply_cpp,"original C wrappers expose their allocated MessageParcel");
    uint64_t option[2]={0,0};option_init(option,0,8);
    int sent=send_request(invoker,0,0x510,request_cpp,reply_cpp,option);
    printf("IPC010_SEND result=%d\n",sent);
    check(sent==0,"original BinderInvoker SendRequest and real kernel reply succeed");
    uint64_t response=0;
    check(parcel_read(reply,&response)==0&&response==0xdef010,"original SDK decodes actual server reply");
    check(own(connection)==self&&own_first(connection)==first,"real SDK transaction preserves own task tokens");
    parcel_destroy(request);parcel_destroy(reply);
    printf("IPC010_TRANSACTION_PASS original_parcel=1 original_invoker=1 authentic_sender_checked=1 reply_verified=1 services_not_tested=1\n");
'''
sdk_source=sdk_source.replace(anchor,client+anchor)
payload=parent['payload'];payload=payload[payload.index('\nfrom pathlib import Path')+1:]
payload='source='+repr(source)+'\nsdk_source='+repr(sdk_source)+'\n'+payload
payload=payload.replace('baremetal-identity-native-read-009','baremetal-identity-ipc-transactions-010')
anchor="pending=['libipc_common.z.so'];visited=set()"
assert payload.count(anchor)==1
payload=payload.replace(anchor,"pending=['libipc_common.z.so','libipc_capi.z.so'];visited=set()")
compile(payload,'prepare-ipc-transactions-010','exec')
if __name__=='__main__':
    result=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=300)
    raise SystemExit(result.returncode)
