"""Exercise changed DHCP leases and exact diagnostic-only SSH config binding."""
from pathlib import Path
import subprocess
import tempfile
import unittest

BASE = Path(__file__).resolve().parent


class DynamicAddress(unittest.TestCase):
    def test_address_selection_and_config_preservation(self):
        with tempfile.TemporaryDirectory(prefix='address159-') as directory:
            root = Path(directory)
            config = 'Port 22257\nListenAddress 192.168.10.210\nAuthenticationMethods publickey\nDisableForwarding yes\nForceCommand read-only\n'
            (root / 'input').write_text(config)
            (root / 'ambiguous').write_text(config + '\tlistenaddress 0.0.0.0\n')
            test = '#define _GNU_SOURCE\n#include "' + str(BASE / 'live-debug-address-159.h') + '"\n'
            test += r'''
int main(int argc,char **argv) {
 if(argc!=5)return 1;
 struct sockaddr_in first={.sin_family=AF_INET}, second={.sin_family=AF_INET};
 inet_pton(AF_INET,"192.168.10.142",&first.sin_addr);
 inet_pton(AF_INET,"192.168.10.210",&second.sin_addr);
 struct ifaddrs other={.ifa_name="wlan0",.ifa_flags=IFF_UP,.ifa_addr=(struct sockaddr*)&second};
 struct ifaddrs actual={.ifa_name="wlan0",.ifa_flags=IFF_UP,.ifa_addr=(struct sockaddr*)&first};
 char address[INET_ADDRSTRLEN];
 if(live_address159_select(&actual,address) || strcmp(address,"192.168.10.142"))return 2;
 actual.ifa_next=&other;
 if(!live_address159_select(&actual,address))return 3;
 actual.ifa_next=NULL;
 actual.ifa_name="eth0";
 if(!live_address159_select(&actual,address))return 4;
 actual.ifa_name="wlan0";actual.ifa_flags=0;
 if(!live_address159_select(&actual,address))return 5;
 if(live_address159_allowed("0.0.0.0") || live_address159_allowed("192.168.10.255") ||
    live_address159_allowed("192.168.10.142\nPasswordAuthentication yes") ||
    live_address159_allowed("127.0.0.1"))return 6;
 if(live_address159_config(argv[1],argv[2],"192.168.10.142"))return 7;
 if(!live_address159_config(argv[1],argv[2],"192.168.10.142"))return 8;
 if(!live_address159_config(argv[3],argv[4],"192.168.10.142"))return 9;
 return 0;
}
'''
            (root / 'test.c').write_text(test)
            compiled = subprocess.run(['cc','-Wall','-Wextra','-Werror',str(root / 'test.c'),'-o',str(root / 'test')],capture_output=True,text=True)
            self.assertEqual(compiled.returncode,0,compiled.stderr)
            self.assertEqual(subprocess.run([str(root / 'test'),str(root / 'input'),str(root / 'output'),str(root / 'ambiguous'),str(root / 'bad-output')],timeout=5).returncode,0)
            self.assertEqual((root / 'input').read_text(),config)
            self.assertEqual((root / 'output').read_text(),config.replace('192.168.10.210','192.168.10.142'))
            self.assertEqual((root / 'output').stat().st_mode & 0o777,0o600)
            self.assertFalse((root / 'bad-output').exists())


if __name__ == '__main__':
    unittest.main()
