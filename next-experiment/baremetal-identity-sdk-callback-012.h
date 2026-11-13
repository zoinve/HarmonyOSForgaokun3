/* Test-only receiver reached through the original SDK's Binder dispatch. */
struct sdk_callback_012 {
    int (*read)(const void *,uint64_t *);
    int (*write)(void *,uint64_t);
    uint64_t (*calling)(void),(*first)(void),(*pid)(void),(*uid)(void),(*self)(void);
    int (*handling)(void);
    unsigned count;
};
static int sdk_callback_012(uint32_t code,const void *data,void *reply,void *opaque)
{
    struct sdk_callback_012 *ctx=opaque;
    check(ctx&&ctx->count==0,"one original SDK nested callback");
    check(code==0x512,"original SDK callback code");
    uint64_t value=0;
    check(ctx->read(data,&value)==0&&value==0xcafe012,"original SDK callback reads actual request parcel");
    check(ctx->handling()==1,"original SDK marks real incoming transaction context");
    check(ctx->calling()==0x1122334455667788ULL&&ctx->first()==0x8877665544332211ULL,
          "original SDK exposes authentic caller and first-caller full tokens");
    check(ctx->pid()==1&&ctx->uid()==0,"original SDK exposes actual callback sender PID and UID");
    check(ctx->self()==0x5000000000000500ULL,"original SDK receiver retains its own task token");
    check(ctx->write(reply,0xbeef012)==0,"original SDK writes real callback reply");
    ++ctx->count;
    printf("IPC012_CALLBACK_PASS original_dispatch=1 calling_full_token=1 first_full_token=1 pid_uid=1 self_preserved=1\n");
    return 0;
}
