"""Protocol validation does not imply network reachability or SSH authentication."""
from pathlib import Path
import subprocess
import tempfile
import unittest

BASE = Path(__file__).resolve().parent


class DiscoveryProtocol(unittest.TestCase):
    def test_fixed_protocol_and_peer_limits(self):
        with tempfile.TemporaryDirectory(prefix='discovery159-') as directory:
            root = Path(directory)
            source = '#define _GNU_SOURCE\n#include "' + str(BASE / 'live-debug-discovery-159.h') + '"\n'
            source += r'''
int main(void) {
 char query[128], nonce[33];
 memset(query,' ',sizeof(query));
 memcpy(query,DISCOVERY159_PREFIX,sizeof(DISCOVERY159_PREFIX)-1);
 const size_t offset=sizeof(DISCOVERY159_PREFIX)-1;
 memcpy(query+offset,"0123456789abcdef0123456789abcdef",32);
 query[127]='\n';
 if(discovery159_nonce(query,sizeof(query),nonce) || strcmp(nonce,"0123456789abcdef0123456789abcdef"))return 1;
 if(!discovery159_nonce(query,127,nonce))return 2;
 query[offset]='G'; if(!discovery159_nonce(query,128,nonce))return 3; query[offset]='0';
 query[100]='x'; if(!discovery159_nonce(query,128,nonce))return 4; query[100]=' ';
 query[127]=0; if(!discovery159_nonce(query,128,nonce))return 5;
 struct sockaddr_in peer={.sin_family=AF_INET,.sin_port=htons(43000)};
 inet_pton(AF_INET,"192.168.10.201",&peer.sin_addr); if(!discovery159_peer(&peer))return 6;
 inet_pton(AF_INET,"192.168.10.248",&peer.sin_addr); if(!discovery159_peer(&peer))return 7;
 inet_pton(AF_INET,"192.168.10.128",&peer.sin_addr); if(discovery159_peer(&peer))return 8;
 inet_pton(AF_INET,"192.168.10.201",&peer.sin_addr); peer.sin_port=htons(53);
 if(discovery159_peer(&peer))return 9;
 if(discovery159_open("not-an-interface")!=-1)return 10;
 unsigned remaining=1;time_t last=0;
 if(discovery159_step(-1,1,"192.168.10.128",&remaining,&last)!=-1)return 11;
 return 0;
}
'''
            (root / 'test.c').write_text(source)
            compiled = subprocess.run(['cc', '-Wall', '-Wextra', '-Werror', str(root / 'test.c'), '-o', str(root / 'test')], capture_output=True, text=True)
            self.assertEqual(compiled.returncode, 0, compiled.stderr)
            self.assertEqual(subprocess.run([str(root / 'test')], timeout=5).returncode, 0)


if __name__ == '__main__':
    unittest.main()
