from ctypes import *
from ctypes.wintypes import *
import ctypes
import psutil
import time

_TH32CS_SNAPMODULE = 0x00000008

class MODULEENTRY32(Structure):
    _fields_ = [
        ('dwSize', DWORD),
        ('th32ModuleID', DWORD),
        ('th32ProcessID', DWORD),
        ('GlblcntUsage', DWORD),
        ('ProccntUsage', DWORD),
        ('modBaseAddr', POINTER(BYTE)),
        ('modBaseSize', DWORD),
        ('hModule', HMODULE),
        ('szModule' , c_char * 260 ),
        ('szExePath' , c_char * 260 ),
        ('dwFlags', DWORD)
    ]

class MemoryReader():

    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_VM_READ = 0x0010

    def __init__(self, process_name: str):
        self.process_name = process_name
        self.pid = self.get_client_pid(self.process_name)
        self.proc = windll.kernel32.OpenProcess(self.PROCESS_QUERY_INFORMATION|self.PROCESS_VM_READ,False,self.pid)
        self.base = self.get_base()

    @staticmethod
    def get_client_pid(process_name):
        pid = None
        for proc in psutil.process_iter():
            if proc.name() == process_name:
                pid = int(proc.pid)
                break
        return pid
    
    def get_base(self):
        kernel32                 = windll.kernel32
        CreateToolhelp32Snapshot = kernel32.CreateToolhelp32Snapshot
        CloseHandle              = kernel32.CloseHandle
        Module32First            = kernel32.Module32First

        me32 = MODULEENTRY32()
        me32.dwSize = sizeof(MODULEENTRY32)
        hProcessSnap = CreateToolhelp32Snapshot(_TH32CS_SNAPMODULE, self.pid)

        ret = None
        if Module32First(hProcessSnap, byref(me32)):
            ret = ctypes.addressof(me32.modBaseAddr.contents)
        CloseHandle(hProcessSnap)
        return ret

    def read(self, addr):
        readprocess = windll.kernel32.ReadProcessMemory
        rdbuf = ctypes.c_uint()
        bytread = ctypes.c_size_t()
        try:
            if readprocess(self.proc, ctypes.c_void_p(addr), ctypes.byref(rdbuf), ctypes.sizeof(rdbuf),ctypes.byref(bytread)):
                return rdbuf.value
        except Exception as e:
            print("ERROR", e)

    def read_string(self, addr, size_of_data=64):
        readprocess = windll.kernel32.ReadProcessMemory
        rdbuf = create_string_buffer(size_of_data)
        bytread = ctypes.c_size_t()
        try:
            if readprocess(self.proc, ctypes.c_void_p(addr), ctypes.byref(rdbuf), ctypes.sizeof(rdbuf),ctypes.byref(bytread)):
                return rdbuf.value.decode()
        except Exception as e:
            print("ERROR", e)

    def read_pointer(self, addr, offsets):
        _addr = self.read(addr)
        for offset in offsets:
            _addr = _addr + offset
            _addr = self.read(_addr)

        return _addr
        

if __name__ == "__main__":
    mr = MemoryReader("Rocksmith2014.exe")
    print(mr.get_base())

    print(mr.read_string(mr.read_pointer(mr.get_base() + 0x00F5C494, [0xBC])))