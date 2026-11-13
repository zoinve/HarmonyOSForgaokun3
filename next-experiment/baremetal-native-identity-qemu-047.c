/* Diskless QEMU-only harness. Never becomes part of a board boot entry. */
#define _GNU_SOURCE
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mount.h>
#include <sys/reboot.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <unistd.h>

static void finish(int ok)
{
    printf("NATIVE_READ047_%s desktop_not_tested=1 policy_not_loaded=1\n",ok?"PASS":"FAIL");
    fflush(NULL);sync();reboot(RB_POWER_OFF);for(;;)pause();
}
#define CHECK(c) do {if(!(c)){perror(#c);finish(0);}} while(0)
int main(void)
{
    if(getpid()!=1||geteuid()!=0)return 77;
    CHECK(!mount("proc","/proc","proc",MS_NODEV|MS_NOSUID|MS_NOEXEC,NULL));
    char command[4096]={0};int fd=open("/proc/cmdline",O_RDONLY);
    CHECK(fd>=0&&read(fd,command,sizeof(command)-1)>0);close(fd);
    CHECK(strstr(command," harmony.identity_read_test=1 "));
    CHECK(strstr(command," enforcing=1 "));
    CHECK(!mount("sysfs","/sys","sysfs",MS_NODEV|MS_NOSUID|MS_NOEXEC,NULL));
    char model[128]={0};fd=open("/sys/firmware/devicetree/base/model",O_RDONLY);
    CHECK(fd>=0&&read(fd,model,sizeof(model)-1)>0);close(fd);
    CHECK(strstr(model,"dummy-virt"));
    CHECK(!mount("devtmpfs","/dev","devtmpfs",MS_NOSUID|MS_NOEXEC,NULL));
    int refusal=strstr(command," harmony.expect_refusal=1 ")!=NULL;
    pid_t child=fork();CHECK(child>=0);
    if(!child){execl("/probe","/probe",NULL);_exit(126);}
    int status=0;CHECK(waitpid(child,&status,0)==child);
    CHECK(WIFEXITED(status)&&WEXITSTATUS(status)==(refusal?77:0));
    CHECK(access("/run/identity-read-002",F_OK)==-1);
    printf("NATIVE_READ047_RESULT expected_refusal=%d child_status=%d mountpoint_removed=1\n",refusal,WEXITSTATUS(status));
    finish(1);return 0;
}
