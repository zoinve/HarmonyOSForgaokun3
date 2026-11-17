"""Compile exact network observer with no real interfaces or file access."""
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest

NETWORK = runpy.run_path(str(Path(__file__).with_name('commercial-network-helper-084.py')))['NETWORK']
STUB = r'''
#define _GNU_SOURCE
#include <arpa/inet.h>
#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <ifaddrs.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
static int scenario, opens, reads, bytes;
static struct ifaddrs entries[65];
static struct sockaddr_in address, mask;
static struct sockaddr_in6 address6, mask6;
static int mock_getifaddrs(struct ifaddrs **head)
{
    if(scenario==1){errno=EIO;return -1;}
    memset(entries,0,sizeof(entries));
    address.sin_family=mask.sin_family=AF_INET;
    assert(inet_pton(AF_INET,"192.0.2.2",&address.sin_addr)==1);
    assert(inet_pton(AF_INET,"255.255.255.0",&mask.sin_addr)==1);
    address6.sin6_family=mask6.sin6_family=AF_INET6;
    assert(inet_pton(AF_INET6,"2001:db8::2",&address6.sin6_addr)==1);
    assert(inet_pton(AF_INET6,"ffff:ffff:ffff:ffff::",&mask6.sin6_addr)==1);
    int count=scenario==4 ? 65 : 1;
    for(int i=0;i<count;++i){
        entries[i].ifa_name="wlan0";
        entries[i].ifa_addr=scenario==2 ? NULL : (struct sockaddr *)&address;
        entries[i].ifa_netmask=(struct sockaddr *)&mask;
        if(scenario==5){entries[i].ifa_addr=(struct sockaddr *)&address6;entries[i].ifa_netmask=(struct sockaddr *)&mask6;}
        entries[i].ifa_next=i+1<count ? &entries[i+1] : NULL;
    }
    *head=entries;return 0;
}
static void mock_freeifaddrs(struct ifaddrs *head){assert(head==entries);}
static int mock_open(const char *path,int flags,...)
{
    const char *allowed[]={"/proc/net/route","/proc/net/ipv6_route","/sys/class/net/wlan0/carrier",
        "/sys/class/net/wlan0/operstate","/data/local/tmp/l410-wifi-compat-v2/netmanager-v4.status",
        "/data/local/tmp/l410-wifi-compat-v2/natural-control-v6.status",
        "/data/service/el1/public/dhcp/dhcp_cache.conf"};
    assert(opens<7 && !strcmp(path,allowed[opens]));++opens;
    assert(flags==(O_RDONLY|O_CLOEXEC|O_NOFOLLOW));
    if(scenario!=3 && scenario!=6){errno=ENOENT;return -1;}return 42;
}
static int mock_fstat(int fd,struct stat *out)
{assert(fd==42);memset(out,0,sizeof(*out));out->st_mode=scenario==6 ? S_IFSOCK : S_IFREG;return 0;}
static ssize_t mock_read(int fd,void *buffer,size_t size)
{assert(fd==42 && size==4096);++reads;memset(buffer,'x',size);return (ssize_t)size;}
static ssize_t mock_write(int fd,const void *buffer,size_t size)
{assert(fd==1 && buffer);bytes+=(int)size;return (ssize_t)size;}
static int mock_close(int fd){assert(fd==42);return 0;}
#define getifaddrs(...) mock_getifaddrs(__VA_ARGS__)
#define freeifaddrs(...) mock_freeifaddrs(__VA_ARGS__)
#define open(...) mock_open(__VA_ARGS__)
#define fstat(...) mock_fstat(__VA_ARGS__)
#define read(...) mock_read(__VA_ARGS__)
#define write(...) mock_write(__VA_ARGS__)
#define close(...) mock_close(__VA_ARGS__)
'''
MAIN = r'''
int main(int argc,char **argv)
{
    assert(argc==2);scenario=atoi(argv[1]);int rc=network084_observe();
    printf("RESULT rc=%d opens=%d reads=%d bytes=%d\n",rc,opens,reads,bytes);return 0;
}
'''


class ObserverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        root = Path(cls.temp.name)
        source = root / 'test.c'
        source.write_text(STUB + NETWORK + MAIN)
        cls.exe = root / 'test'
        subprocess.run(['gcc', '-O2', '-Wall', '-Wextra', '-Werror', str(source), '-o', str(cls.exe)], check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def case(self, scenario):
        return subprocess.run([str(self.exe), str(scenario)], check=True, capture_output=True, text=True, timeout=3).stdout

    def test_actual_ipv4_conversion(self):
        self.assertIn('family=2 value=192.0.2.2 netmask=255.255.255.0', self.case(0))

    def test_actual_ipv6_conversion(self):
        self.assertIn('family=10 value=2001:db8::2 netmask=ffff:ffff:ffff:ffff::', self.case(5))

    def test_interface_enumeration_error_does_not_invent_data(self):
        self.assertIn('rc=90 opens=0 reads=0 bytes=0', self.case(1))

    def test_null_address_is_ignored(self):
        self.assertNotIn('NETWORK084_ADDRESS', self.case(2))

    def test_interface_limit_is_64(self):
        self.assertEqual(self.case(4).count('NETWORK084_ADDRESS'), 64)

    def test_fixed_file_allowlist_and_read_bounds(self):
        self.assertIn('rc=0 opens=7 reads=28 bytes=114688', self.case(3))

    def test_nonregular_files_not_read(self):
        self.assertIn('rc=0 opens=7 reads=0 bytes=0', self.case(6))


if __name__ == '__main__':
    unittest.main()
