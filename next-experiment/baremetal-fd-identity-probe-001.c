#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <unistd.h>

int main(void)
{
    if (getuid()!=1001 || geteuid()!=1001 || prctl(PR_GET_NO_NEW_PRIVS,0,0,0,0)!=1)
        return 77;
    int first=open("/dev/null",O_RDWR|O_CLOEXEC);
    int duplicate=first<0?-1:dup(first);
    int independent=open("/dev/null",O_RDWR|O_CLOEXEC);
    if (first<0 || duplicate<0 || independent<0) return 1;
    errno=0;
    long same=syscall(SYS_kcmp,getpid(),getpid(),0,first,duplicate);
    int same_errno=errno;
    errno=0;
    long different=syscall(SYS_kcmp,getpid(),getpid(),0,first,independent);
    int different_errno=errno;
    /* F_DUPFD_QUERY is a separate diagnostic, not a guessed replacement for kcmp. */
    errno=0;
    long query_same=syscall(SYS_fcntl,first,1027,duplicate);
    int query_same_errno=errno;
    errno=0;
    long query_different=syscall(SYS_fcntl,first,1027,independent);
    int query_different_errno=errno;
    printf("FD_IDENTITY001 uid=%u nnp=1 kcmp_duplicate=%ld errno=%d kcmp_independent=%ld errno=%d "
           "query_duplicate=%ld errno=%d query_independent=%ld errno=%d gpu_tested=0\n",
           (unsigned)getuid(),same,same_errno,different,different_errno,
           query_same,query_same_errno,query_different,query_different_errno);
    close(first);close(duplicate);close(independent);
    if (same!=0 || same_errno || different<=0 || different_errno) return 1;
    puts("FD_IDENTITY001_PASS actual_kcmp_distinguishes_file_descriptions=1");
    return 0;
}
