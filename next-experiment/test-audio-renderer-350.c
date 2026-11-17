#define main audio350_program_main
#include "native-audio-renderer-350.c"
#undef main
#include <assert.h>
int main(void)
{
    struct audio350_context context={0};audio350_wave(&context);
    unsigned char data[1920];
    for(unsigned block=0;block<50;++block)
        assert(audio350_write(NULL,&context,data,sizeof(data))==AUDIO_DATA_CALLBACK_RESULT_VALID);
    assert(atomic_load(&context.cursor)==24000&&atomic_load(&context.callbacks)==50);
    uint64_t nonzero=atomic_load(&context.nonzero_frames);
    assert(nonzero>9000&&nonzero<9600);
    for(unsigned i=0;i<sizeof(data);++i)assert(!data[i]);
    assert(audio350_write(NULL,&context,data,3)==AUDIO_DATA_CALLBACK_RESULT_INVALID);
    assert(atomic_load(&context.invalid_buffers)==1);
    for(unsigned i=0;i<1200;++i)assert(context.wave[i]>=-256&&context.wave[i]<=256);
    puts("AUDIO350_TEST passed=1 tone_bounded_and_faded=1 synthetic_fixture_only=1 acoustic_output_verified=0");
    return 0;
}
