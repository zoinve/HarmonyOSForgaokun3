"""Ask the original RS for public screen/tree diagnostics; no synthetic nodes."""
HELPER=r'''
static void commercial_rs_tree034(unsigned sample)
{
    if(sample!=10)return;
    /* MultiRSTrees requests the normal tree dump without forcing a single frame.
       Both original hidumper commands use the existing 3-second child deadline.
       A killed client need not cancel a queued service-side diagnostic task. */
    const char *queries[]={"screen","MultiRSTrees"};
    for(unsigned i=0;i<2;++i){
        dprintf(commercial_diag_fd003,"COMMERCIAL034_RS_DUMP_BEGIN sample=%u service=10 query=%s desktop_verified=0\n",sample,queries[i]);
        char *args[]={(char*)"/system/bin/hidumper",(char*)"-s",(char*)"10",(char*)"-a",(char*)queries[i],NULL};
        commercial_command002(args);
        dprintf(commercial_diag_fd003,"COMMERCIAL034_RS_DUMP_END sample=%u service=10 query=%s\n",sample,queries[i]);
    }
}
'''
def instrument(original):
    assert 'COMMERCIAL034_RS_DUMP' not in original
    anchor='static void commercial_capture016(unsigned);'
    call='        commercial_capture016(sample);'
    assert original.count(anchor)==original.count(call)==1
    assert 'n<30' in original and 'usleep(100000)' in original and 'kill(p,SIGKILL)' in original
    return original.replace(anchor,HELPER+anchor,1).replace(call,call+'\n        commercial_rs_tree034(sample);',1)
