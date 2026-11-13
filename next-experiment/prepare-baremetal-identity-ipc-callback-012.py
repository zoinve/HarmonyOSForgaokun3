"""Extend original SDK SendRequest with a genuine nested SDK callback receiver."""
from pathlib import Path
import runpy
import subprocess

base=Path(__file__).resolve().parent
parent=runpy.run_path(str(base/'prepare-baremetal-identity-ipc-transactions-011.py'))
source=parent['source'].replace('IDENTITY011_','IDENTITY012_').replace('IPC011_','IPC012_')
anchor='sdk_request.data_size==8'
assert source.count(anchor)==1
source=source.replace(anchor,'sdk_request.data_size>=8&&sdk_request.offsets_size==sizeof(binder_size_t)')
anchor='    uint64_t sdk_response=0xdef010;'
assert source.count(anchor)==1
nested=r'''    binder_size_t object_offset=*(binder_size_t *)(uintptr_t)sdk_request.data.ptr.offsets;
    require(object_offset<=sdk_request.data_size&&sizeof(struct flat_binder_object)<=sdk_request.data_size-object_offset,
            "kernel translated original SDK callback object is bounded");
    struct flat_binder_object object;
    memcpy(&object,(void *)(uintptr_t)(sdk_request.data.ptr.buffer+object_offset),sizeof(object));
    require(object.hdr.type==BINDER_TYPE_HANDLE,"original SDK callback object translated to remote handle");
    uint64_t nested_payload=0xcafe012;
    struct binder_transaction_data nested_request={.target.handle=object.handle,.code=0x512,
        .data_size=sizeof(nested_payload),.data.ptr.buffer=(uintptr_t)&nested_payload};
    binder_write_003(binder,BC_TRANSACTION,&nested_request,sizeof(nested_request));
    struct binder_transaction_data nested_reply=binder_next_003(&sdk_reader,BR_REPLY);
    require(nested_reply.data_size==8&&*(uint64_t *)(uintptr_t)nested_reply.data.ptr.buffer==0xbeef012,
            "original SDK callback returns actual parcel reply");
    binder_identity_003(binder,0x5000000000000500ULL,0x6000000000000600ULL,sdk_child);
    binder_write_003(binder,BC_FREE_BUFFER,&nested_reply.data.ptr.buffer,sizeof(binder_uintptr_t));
'''
source=source.replace(anchor,nested+anchor)
sdk_source=parent['sdk_source'].replace('SDK011_','SDK012_').replace('IPC011_','IPC012_')
anchor='int main(void)'
assert sdk_source.count(anchor)==1
sdk_source=sdk_source.replace(anchor,(base/'baremetal-identity-sdk-callback-012.h').read_text()+'\n'+anchor)
anchor='    /* Test adapter for the exact hashed SDK DSO:'
assert sdk_source.count(anchor)==1
setup=r'''    void *(*stub_create)(const char *,int (*)(uint32_t,const void *,void *,void *),void (*)(void *),void *)=
        dlsym(capi,"OH_IPCRemoteStub_Create");
    void (*stub_destroy)(void *)=dlsym(capi,"OH_IPCRemoteStub_Destroy");
    int (*write_stub)(void *,void *)=dlsym(capi,"OH_IPCParcel_WriteRemoteStub");
    struct sdk_callback_012 callback={.read=parcel_read,.write=parcel_write};
    callback.calling=dlsym(capi,"OH_IPCSkeleton_GetCallingTokenId");
    callback.first=dlsym(capi,"OH_IPCSkeleton_GetFirstTokenId");
    callback.pid=dlsym(capi,"OH_IPCSkeleton_GetCallingPid");
    callback.uid=dlsym(capi,"OH_IPCSkeleton_GetCallingUid");
    callback.self=dlsym(capi,"OH_IPCSkeleton_GetSelfTokenId");
    callback.handling=dlsym(capi,"OH_IPCSkeleton_IsHandlingTransaction");
    check(stub_create&&stub_destroy&&write_stub&&callback.calling&&callback.first&&callback.pid&&
          callback.uid&&callback.self&&callback.handling,"resolve original SDK stub and calling-context APIs");
    void *stub=stub_create("harmony.lab.identity012",sdk_callback_012,NULL,&callback);
    check(stub&&write_stub(request,stub)==0,"original SDK exports genuine callback object through parcel");
'''
sdk_source=sdk_source.replace(anchor,setup+anchor)
anchor='    parcel_destroy(request);parcel_destroy(reply);'
assert sdk_source.count(anchor)==1
sdk_source=sdk_source.replace(anchor,r'''    check(callback.count==1,"original SDK received nested callback before outer SendRequest returned");
    check(!callback.handling()&&callback.calling()==self&&callback.first()==first&&
          callback.pid()==(uint64_t)getpid()&&callback.uid()==(uint64_t)getuid(),
          "original SDK restores outside-transaction identity after callback");
    printf("IPC012_CALLBACK_RESTORE_PASS outside_context=1 full_tokens=1 pid_uid=1\n");
    parcel_destroy(request);parcel_destroy(reply);stub_destroy(stub);''')
payload=parent['payload'];payload=payload[payload.index('\nfrom pathlib import Path')+1:]
payload='source='+repr(source)+'\nsdk_source='+repr(sdk_source)+'\n'+payload
payload=payload.replace('baremetal-identity-ipc-transactions-011','baremetal-identity-ipc-callback-012')
compile(payload,'prepare-ipc-callback-012','exec')
if __name__=='__main__':
    result=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=300)
    raise SystemExit(result.returncode)
