"""Exact argv checks with mocked effects; no host networking or daemon starts."""
from pathlib import Path
import importlib.util
import runpy
import unittest

b = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('commands083', b / 'test-network-supplicant-083.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.SOURCE = runpy.run_path(str(b / 'commercial-network-helper-085.py'))['SOURCE']
module.STUB = module.STUB.replace('-c/network083/wpa.conf', '-c/network084/wpa.conf')
anchor = '    assert(!strcmp(path,"/network083/lib/ld-linux-aarch64.so.1"));'
replacement = r'''
    if (!strcmp(path,"/system/bin/curl")) {
        const char *fixed[]={"/system/bin/curl","--silent","--show-error","--noproxy","*",
            "--connect-timeout","2","--max-time","4","--output","/dev/null","--write-out",
            "NETWORK085_CURL http_code=%{http_code} remote_ip=%{remote_ip} namelookup=%{time_namelookup} ssl_verify_result=%{ssl_verify_result}\n"};
        for(unsigned i=0;i<sizeof(fixed)/sizeof(fixed[0]);++i)assert(!strcmp(args[i],fixed[i]));
        assert(!strcmp(args[13],"http://connectivitycheck.platform.hicloud.com/generate_204") ||
               !strcmp(args[13],"https://connectivitycheck.platform.hicloud.com/generate_204"));
        assert(!args[14]); ++executed; errno=ENOENT; return -1;
    }
'''
assert module.STUB.count(anchor) == 1
module.STUB = module.STUB.replace(anchor, replacement + anchor, 1)


class ProbeTests(module.CommandTests):
    def test_fixed_probes_have_no_mutations(self):
        for mode in ('http', 'https'):
            output = self.case(mode)
            self.assertIn('rc=87 mutations=0 executed=1', output)
            self.assertIn('tls_bypass=0 success_not_inferred=1', output)

    def test_untrusted_probe_modes_rejected(self):
        for mode in ('https --insecure', 'http://example.com', 'curl', 'https;id'):
            self.assertIn('rc=64 mutations=0 executed=0', self.case(mode))


if __name__ == '__main__':
    unittest.main()
