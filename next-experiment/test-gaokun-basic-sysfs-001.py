"""Exercise the hardware backend against temporary sysfs fixtures only."""
from pathlib import Path
import ctypes
import errno
import subprocess
import tempfile
import unittest

BASE=Path(__file__).resolve().parent

class Battery(ctypes.Structure):
    _fields_=[('valid',ctypes.c_uint32),('present',ctypes.c_int),('capacity',ctypes.c_int),
              ('status',ctypes.c_int),('voltage',ctypes.c_int64),('current',ctypes.c_int64),
              ('temperature',ctypes.c_int64)]

class SysfsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.build=tempfile.TemporaryDirectory(prefix='gaokun-sysfs-build-')
        target=Path(cls.build.name)/'backend.so'
        subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-fPIC','-shared',
                        str(BASE/'gaokun-basic-sysfs-001.c'),'-o',str(target)],check=True)
        cls.lib=ctypes.CDLL(str(target))
        cls.lib.gaokun_battery_read.argtypes=[ctypes.c_char_p,ctypes.POINTER(Battery)]
        cls.lib.gaokun_backlight_get.argtypes=[ctypes.c_char_p,ctypes.POINTER(ctypes.c_uint32)]
        cls.lib.gaokun_backlight_set.argtypes=[ctypes.c_char_p,ctypes.c_uint32]
        cls.lib.gaokun_backlight_get_range.argtypes=[ctypes.c_char_p,ctypes.c_uint32,ctypes.POINTER(ctypes.c_uint32)]
        cls.lib.gaokun_backlight_set_range.argtypes=[ctypes.c_char_p,ctypes.c_uint32,ctypes.c_uint32]

    @classmethod
    def tearDownClass(cls): cls.build.cleanup()

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='gaokun-sysfs-test-')
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.path=str(self.root).encode()

    def fixture(self,**fields):
        for key,value in fields.items(): (self.root/key).write_text(str(value)+'\n')

    def test_real_battery_units_and_negative_current(self):
        self.fixture(type='Battery',present=1,capacity=98,status='Full',voltage_now=8298000,current_now=-1234)
        value=Battery()
        self.assertEqual(self.lib.gaokun_battery_read(self.path,ctypes.byref(value)),0)
        self.assertEqual(value.valid,31)
        self.assertEqual((value.capacity,value.status,value.voltage,value.current),(98,4,8298000,-1234))
        self.assertFalse(value.valid&32)

    def test_missing_and_invalid_values_are_not_successful_measurements(self):
        self.fixture(type='Battery',capacity='100junk',status='Invented',present=3,voltage_now=-1)
        value=Battery()
        self.assertEqual(self.lib.gaokun_battery_read(self.path,ctypes.byref(value)),-errno.ENODATA)
        self.assertEqual(value.valid,0)

    def test_supply_type_and_empty_files(self):
        self.fixture(type='USB',capacity=100)
        self.assertEqual(self.lib.gaokun_battery_read(self.path,ctypes.byref(Battery())),-errno.ENODEV)
        self.fixture(type='Battery',capacity='')
        self.assertEqual(self.lib.gaokun_battery_read(self.path,ctypes.byref(Battery())),-errno.ENODATA)

    def test_backlight_scaling_and_write(self):
        self.fixture(max_brightness=4095,brightness=204)
        value=ctypes.c_uint32()
        self.assertEqual(self.lib.gaokun_backlight_get(self.path,ctypes.byref(value)),0)
        self.assertEqual(value.value,13)
        self.assertEqual(self.lib.gaokun_backlight_set(self.path,255),0)
        self.assertEqual((self.root/'brightness').read_text(),'4095\n')

    def test_backlight_errors_and_overflow(self):
        value=ctypes.c_uint32(88)
        for malformed in ['0','-1','garbage','12bad','4294967296','9'*128]:
            self.fixture(max_brightness=malformed,brightness=1)
            self.assertLess(self.lib.gaokun_backlight_get(self.path,ctypes.byref(value)),0)
            self.assertEqual(value.value,88)
        self.fixture(max_brightness=4095,brightness=4096)
        self.assertEqual(self.lib.gaokun_backlight_get(self.path,ctypes.byref(value)),-errno.ERANGE)
        self.assertEqual(self.lib.gaokun_backlight_set(self.path,256),-errno.ERANGE)

    def test_missing_brightness_is_not_created(self):
        self.fixture(max_brightness=4095)
        self.assertEqual(self.lib.gaokun_backlight_set(self.path,128),-errno.ENOENT)
        self.assertFalse((self.root/'brightness').exists())

    def test_native_hdi_range_is_not_ui_255_range(self):
        self.fixture(max_brightness=4095,brightness=204)
        self.assertEqual(self.lib.gaokun_backlight_set_range(self.path,65535,11363),0)
        self.assertEqual((self.root/'brightness').read_text(),'710\n')
        value=ctypes.c_uint32()
        self.assertEqual(self.lib.gaokun_backlight_get_range(self.path,65535,ctypes.byref(value)),0)
        self.assertEqual(value.value,11363)
        self.assertEqual(self.lib.gaokun_backlight_set_range(self.path,65535,65536),-errno.ERANGE)
        self.assertEqual(self.lib.gaokun_backlight_get_range(self.path,0,ctypes.byref(value)),-errno.EINVAL)
        self.assertEqual(self.lib.gaokun_backlight_set_range(self.path,0,0),-errno.EINVAL)

if __name__=='__main__': unittest.main()
