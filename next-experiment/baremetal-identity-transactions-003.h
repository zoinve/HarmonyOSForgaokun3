/* Test-only raw Binder clients in the guarded, diskless QEMU init. */
#include <sys/mman.h>

struct binder_reader_003 { int fd; unsigned char data[8192]; size_t pos, size; };
static void binder_write_003(int fd, uint32_t command, const void *data, size_t size)
{
    unsigned char bytes[256];
    require(size+sizeof(command)<=sizeof(bytes),"bounded Binder command");
    memcpy(bytes,&command,sizeof(command));memcpy(bytes+sizeof(command),data,size);
    struct binder_write_read wr={.write_size=size+sizeof(command),.write_buffer=(uintptr_t)bytes};
    require(ioctl(fd,BINDER_WRITE_READ,&wr)==0&&wr.write_consumed==wr.write_size,"Binder command consumed");
}
static struct binder_transaction_data binder_next_003(struct binder_reader_003 *reader,uint32_t wanted)
{
    for (;;) {
        if(reader->pos==reader->size) {
            struct binder_write_read wr={.read_size=sizeof(reader->data),.read_buffer=(uintptr_t)reader->data};
            require(ioctl(reader->fd,BINDER_WRITE_READ,&wr)==0&&wr.read_consumed>0,"read actual Binder event");
            reader->pos=0;reader->size=wr.read_consumed;
        }
        require(reader->size-reader->pos>=4,"Binder command header bounded");
        uint32_t command;memcpy(&command,reader->data+reader->pos,4);reader->pos+=4;
        size_t size=_IOC_SIZE(command);
        require(size<=reader->size-reader->pos,"Binder event payload bounded");
        if(command==wanted) {
            struct binder_transaction_data transaction;
            require(size==sizeof(transaction),"Binder transaction layout");
            memcpy(&transaction,reader->data+reader->pos,size);reader->pos+=size;return transaction;
        }
        require(command==BR_NOOP||command==BR_TRANSACTION_COMPLETE,"no failed or unexpected Binder event");
        reader->pos+=size;
    }
}
static void binder_identity_003(int binder,uint64_t token,uint64_t first,pid_t pid)
{
    struct sender_info info;memset(&info,0xa5,sizeof(info));
    require(ioctl(binder,SENDER,&info)==0,"transaction sender-info query");
    require(info.tokens.sender==token&&info.tokens.first==first&&info.pid==(uint64_t)pid,
            "actual transaction token, first-caller and PID match sender");
    require(info.tokens.reserved[0]==0&&info.tokens.reserved[1]==0,"transaction reserved fields zero");
    struct token_pair pair;memset(&pair,0xa5,sizeof(pair));
    require(ioctl(binder,TOKENS,&pair)==0&&pair.sender==token&&pair.first==first&&
            pair.reserved[0]==0&&pair.reserved[1]==0,"both Binder identity interfaces agree");
}
static void binder_transactions_003(int manager,int token_fd)
{
    const uint64_t server_token=0x1122334455667788ULL,server_first=0x8877665544332211ULL;
    pid_t server_pid=getpid();
    require(chmod("/dev/binderfs/identity002",0666)==0,"private test Binder device accessible to test UID");
    void *mapping=mmap(NULL,1024*1024,PROT_READ,MAP_PRIVATE,manager,0);
    require(mapping!=MAP_FAILED,"manager Binder mapping");
    int zero=0;require(ioctl(manager,BINDER_SET_CONTEXT_MGR,&zero)==0,"isolated test context manager");
    binder_write_003(manager,BC_ENTER_LOOPER,&zero,0);
    struct binder_reader_003 reader={.fd=manager};
    for(unsigned iteration=0;iteration<3;iteration++) {
        uint64_t child_token=0x1000000000000100ULL+iteration,child_first=0x2000000000000200ULL+iteration;
        pid_t child=fork();require(child>=0,"fork independent Binder caller");
        if(!child) {
            close(manager);
            require(ioctl(token_fd,SELF_SET,&child_token)==0&&ioctl(token_fd,FIRST_SET,&child_first)==0,"authorized test caller identity setup");
            become(1001,77);
            int client=open("/dev/binderfs/identity002",O_RDWR);require(client>=0,"independent client Binder open");
            void *map=mmap(NULL,1024*1024,PROT_READ,MAP_PRIVATE,client,0);require(map!=MAP_FAILED,"client Binder mapping");
            uint64_t message=0xabc000+iteration;
            struct binder_transaction_data transaction={.target.handle=0,.code=0x300+iteration,
                .flags=iteration==2?TF_ONE_WAY:0,.data_size=sizeof(message),.data.ptr.buffer=(uintptr_t)&message};
            binder_write_003(client,BC_TRANSACTION,&transaction,sizeof(transaction));
            if(iteration!=2) {
                struct binder_reader_003 client_reader={.fd=client};
                struct binder_transaction_data reply=binder_next_003(&client_reader,BR_REPLY);
                require(reply.data_size==sizeof(uint64_t)&&*(uint64_t *)(uintptr_t)reply.data.ptr.buffer==message+1,"real synchronous reply payload");
                binder_identity_003(client,server_token,server_first,server_pid);
                uint64_t self=0;require(ioctl(token_fd,SELF_GET,&self)==0&&self==child_token,"received reply does not overwrite own token");
                binder_write_003(client,BC_FREE_BUFFER,&reply.data.ptr.buffer,sizeof(binder_uintptr_t));
            }
            munmap(map,1024*1024);close(client);_exit(0);
        }
        /* For the one-way case, prove delivery after the sender has exited. */
        if(iteration==2)require(child_status(child),"one-way caller exits before receiver reads");
        struct binder_transaction_data transaction=binder_next_003(&reader,BR_TRANSACTION);
        require(transaction.code==0x300+iteration&&transaction.sender_euid==1001&&transaction.data_size==8,"actual caller UID and transaction payload");
        require(*(uint64_t *)(uintptr_t)transaction.data.ptr.buffer==0xabc000+iteration,"caller payload matches iteration");
        binder_identity_003(manager,child_token,child_first,child);
        uint64_t self=0;require(ioctl(token_fd,SELF_GET,&self)==0&&self==server_token,"incoming caller does not overwrite receiver self token");
        if(iteration!=2) {
            uint64_t response=0xabc001+iteration;
            struct binder_transaction_data reply={.data_size=sizeof(response),.data.ptr.buffer=(uintptr_t)&response};
            binder_write_003(manager,BC_REPLY,&reply,sizeof(reply));
        }
        binder_write_003(manager,BC_FREE_BUFFER,&transaction.data.ptr.buffer,sizeof(binder_uintptr_t));
        if(iteration!=2)require(child_status(child),"synchronous caller verified reply identity");
        printf("IDENTITY003_TRANSACTION iteration=%u oneway=%u verified=1\n",iteration,iteration==2);
    }
    munmap(mapping,1024*1024);
}
