import ctypes
import os
from pathlib import Path

class RustIntegration:
    def __init__(self):
        self.lib_path = Path("rust_exploit/target/release/librust_exploit.so")
        self.lib = None
        self._load_library()
        
    def _load_library(self):
        if self.lib_path.exists():
            self.lib = ctypes.CDLL(str(self.lib_path))
            self._setup_functions()
            
    def _setup_functions(self):
        # Define function signatures
        self.lib.rust_exploit_init.argtypes = [ctypes.c_void_p]
        self.lib.rust_exploit_init.restype = ctypes.c_int
        
        self.lib.rust_heap_spray.argtypes = [ctypes.c_void_p]
        self.lib.rust_heap_spray.restype = ctypes.c_int
        
        self.lib.rust_rop_chain.argtypes = [ctypes.c_void_p]
        self.lib.rust_rop_chain.restype = ctypes.c_int

        self.lib.rust_stack_smash.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint64]
        self.lib.rust_stack_smash.restype = ctypes.c_int

        self.lib.rust_get_version.restype = ctypes.c_char_p
        self.lib.rust_check_arch.restype = ctypes.c_int
        
    def run_rust_exploit(self, target_addr, payload):
        if not self.lib:
            return False
            
        class ExploitContext(ctypes.Structure):
            _fields_ = [
                ("target_addr", ctypes.c_void_p),
                ("payload", ctypes.c_void_p),
                ("payload_len", ctypes.c_size_t)
            ]
            
        ctx = ExploitContext()
        ctx.target_addr = target_addr
        ctx.payload = payload
        ctx.payload_len = len(payload)
        
        return self.lib.rust_exploit_init(ctypes.byref(ctx)) == 0
        
    def encode_with_rust(self, data, key=0x41):
        if not self.lib:
            return data
            
        encoded = self.lib.rust_encode(data, len(data), key)
        if encoded:
            # Convert back to Python bytes
            decoded = ctypes.string_at(encoded, len(data))
            self.lib.rust_free_encoded(encoded)
            return bytes(decoded)
        return data

    def get_version(self):
        if not self.lib:
            return "rust-unavailable"
        return self.lib.rust_get_version().decode()

    def check_arch(self):
        if not self.lib:
            return 0
        return self.lib.rust_check_arch()

    def stack_overflow(self, buf_addr, size, ret_addr):
        if not self.lib:
            return False
        return self.lib.rust_stack_smash(buf_addr, size, ret_addr) == 0
