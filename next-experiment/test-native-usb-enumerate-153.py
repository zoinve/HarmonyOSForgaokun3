from pathlib import Path
import subprocess
import tempfile
import unittest

BASE = Path(__file__).resolve().parent
FIXTURE = r'''
#define USB153_NO_MAIN
#include "native-usb-enumerate-153.c"
#include <assert.h>
static int init_status, frees, exits, list_calls;
static ssize_t device_count=2;
static char context, first, second;
static USB153Device *devices[3];
static int init(USB153Context **out) { if(init_status<0)return init_status;*out=(USB153Context *)&context;return 0; }
static void exit_context(USB153Context *p) { assert(p==(USB153Context *)&context);++exits; }
static ssize_t list(USB153Context *p,USB153Device ***out) { assert(p==(USB153Context *)&context);++list_calls;*out=devices;return device_count; }
static void free_list(USB153Device **p,int unref) { assert(p==devices&&unref==1);++frees; }
static uint8_t bus(USB153Device *p) { (void)p;return 5; }
static uint8_t address(USB153Device *p) { return p==(USB153Device *)&first?1:2; }
int main(void) {
 devices[0]=(USB153Device *)&first;devices[1]=(USB153Device *)&second;
 struct usb153_api api={init,exit_context,list,free_list,bus,address};
 assert(usb153_enumerate(&api)==0);assert(frees==1&&exits==1);
 device_count=-3;assert(usb153_enumerate(&api)==82);assert(exits==2);
 device_count=129;assert(usb153_enumerate(&api)==82);assert(exits==3);
 int previous=list_calls;init_status=-1;assert(usb153_enumerate(&api)==80);assert(list_calls==previous);
 return 0;
}
'''


class BackendTests(unittest.TestCase):
    def test_real_source_error_and_count_handling(self):
        with tempfile.TemporaryDirectory(prefix='usb153-') as folder:
            root = Path(folder)
            (root / 'test.c').write_text(FIXTURE)
            compiled = subprocess.run(['gcc', '-O2', '-Wall', '-Wextra', '-Werror', '-I', str(BASE),
                str(root / 'test.c'), '-o', str(root / 'test')], capture_output=True, text=True, timeout=30)
            self.assertEqual(compiled.returncode, 0, compiled.stderr)
            proc = subprocess.run([str(root / 'test')], capture_output=True, text=True, timeout=5)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn('node=/dev/bus/usb/005/002', proc.stdout)
            self.assertIn('USB153_LIST count=-3', proc.stdout)
            self.assertIn('reason=list_error_or_limit', proc.stdout)

    def test_no_transfer_or_identity_apis(self):
        source = (BASE / 'native-usb-enumerate-153.c').read_text()
        for forbidden in ['libusb_open', 'libusb_claim_interface', 'libusb_set_configuration', 'libusb_reset_device',
                          'libusb_get_string_descriptor', 'libusb_control_transfer', 'O_RDWR', 'O_WRONLY']:
            self.assertNotIn(forbidden, source)
        self.assertIn('count > 128', source)
        self.assertIn('return 79', source)


if __name__ == '__main__':
    unittest.main()
