/* Actual nested A -> manager -> A callback, confined to diskless QEMU. */
static void binder_nested_004(int manager,int token_fd)
{
    const uint64_t server_token=0x1122334455667788ULL,server_first=0x8877665544332211ULL;
    const uint64_t child_token=0x3000000000000300ULL,child_first=0x4000000000000400ULL;
    void *mapping=mmap(NULL,1024*1024,PROT_READ,MAP_PRIVATE,manager,0);
    require(mapping!=MAP_FAILED,"nested manager Binder mapping");
    pid_t server_pid=getpid(),child=fork();require(child>=0,"fork nested callback caller");
    if(!child) {
        close(manager);
        require(ioctl(token_fd,SELF_SET,&child_token)==0&&ioctl(token_fd,FIRST_SET,&child_first)==0,"nested caller identity setup");
        become(1001,77);
        int client=open("/dev/binderfs/identity002",O_RDWR);require(client>=0,"nested client Binder open");
        void *map=mmap(NULL,1024*1024,PROT_READ,MAP_PRIVATE,client,0);require(map!=MAP_FAILED,"nested client mapping");
        struct flat_binder_object object={.hdr.type=BINDER_TYPE_BINDER,.binder=0x12340000,.cookie=0x56780000};
        binder_size_t offset=0;
        struct binder_transaction_data transaction={.target.handle=0,.code=0x400,.data_size=sizeof(object),
            .offsets_size=sizeof(offset),.data.ptr.buffer=(uintptr_t)&object,.data.ptr.offsets=(uintptr_t)&offset};
        binder_write_003(client,BC_TRANSACTION,&transaction,sizeof(transaction));
        struct binder_reader_003 reader={.fd=client};
        struct binder_transaction_data callback=binder_next_003(&reader,BR_TRANSACTION);
        require(callback.code==0x401&&callback.target.ptr==object.binder&&callback.cookie==object.cookie&&
            callback.sender_euid==0&&callback.data_size==8,"nested callback target and sender UID");
        require(*(uint64_t *)(uintptr_t)callback.data.ptr.buffer==0xcafe004,"nested callback payload");
        binder_identity_003(client,server_token,server_first,server_pid);
        uint64_t own=0;require(ioctl(token_fd,SELF_GET,&own)==0&&own==child_token,"nested incoming call preserves own token");
        /* An authorized group change distinguishes the callback reply identity from the outer request. */
        uint64_t changed_first=child_first+1;
        require(ioctl(token_fd,FIRST_SET,&changed_first)==0,"nested authorized first-caller change");
        uint64_t response=0xbeef004;
        struct binder_transaction_data reply={.data_size=8,.data.ptr.buffer=(uintptr_t)&response};
        binder_write_003(client,BC_REPLY,&reply,sizeof(reply));
        binder_write_003(client,BC_FREE_BUFFER,&callback.data.ptr.buffer,sizeof(binder_uintptr_t));
        struct binder_transaction_data outer_reply=binder_next_003(&reader,BR_REPLY);
        require(outer_reply.data_size==8&&*(uint64_t *)(uintptr_t)outer_reply.data.ptr.buffer==0xface004,"outer reply after nested callback");
        binder_identity_003(client,server_token,server_first,server_pid);
        require(ioctl(token_fd,SELF_GET,&own)==0&&own==child_token,"outer reply preserves caller self token");
        require(ioctl(token_fd,FIRST_GET,&own)==0&&own==changed_first,"outer reply preserves authorized caller first token");
        binder_write_003(client,BC_FREE_BUFFER,&outer_reply.data.ptr.buffer,sizeof(binder_uintptr_t));
        munmap(map,1024*1024);close(client);_exit(0);
    }
    struct binder_reader_003 reader={.fd=manager};
    struct binder_transaction_data transaction=binder_next_003(&reader,BR_TRANSACTION);
    require(transaction.code==0x400&&transaction.sender_euid==1001&&transaction.data_size==sizeof(struct flat_binder_object)&&
        transaction.offsets_size==sizeof(binder_size_t),"outer callback object transaction");
    binder_identity_003(manager,child_token,child_first,child);
    struct flat_binder_object *object=(void *)(uintptr_t)transaction.data.ptr.buffer;
    require(object->hdr.type==BINDER_TYPE_HANDLE&&object->handle!=0,"kernel translates callback object into handle");
    uint64_t message=0xcafe004;
    struct binder_transaction_data nested={.target.handle=object->handle,.code=0x401,.data_size=8,.data.ptr.buffer=(uintptr_t)&message};
    binder_write_003(manager,BC_TRANSACTION,&nested,sizeof(nested));
    struct binder_transaction_data nested_reply=binder_next_003(&reader,BR_REPLY);
    require(nested_reply.data_size==8&&*(uint64_t *)(uintptr_t)nested_reply.data.ptr.buffer==0xbeef004,"nested callback reply payload");
    binder_identity_003(manager,child_token,child_first+1,child);
    uint64_t own=0;require(ioctl(token_fd,SELF_GET,&own)==0&&own==server_token,"nested reply preserves server self token");
    require(ioctl(token_fd,FIRST_GET,&own)==0&&own==server_first,"nested reply preserves server first token");
    binder_write_003(manager,BC_FREE_BUFFER,&nested_reply.data.ptr.buffer,sizeof(binder_uintptr_t));
    uint64_t response=0xface004;
    struct binder_transaction_data reply={.data_size=8,.data.ptr.buffer=(uintptr_t)&response};
    binder_write_003(manager,BC_REPLY,&reply,sizeof(reply));
    binder_write_003(manager,BC_FREE_BUFFER,&transaction.data.ptr.buffer,sizeof(binder_uintptr_t));
    require(child_status(child),"nested caller verified callback and final reply identities");
    munmap(mapping,1024*1024);
    printf("IDENTITY004_NESTED callback=1 reply_identity_changed=1 self_tokens_preserved=1 verified=1\n");
}
