import os
import subprocess
import platform
from pathlib import Path

class Triage:
    def __init__(self, findings_dir):
        self.findings = Path(findings_dir)
        self.results = {}
        
    def get_crashes(self):
        crash_dir = self.findings / "default" / "crashes"
        if platform.system() == "Windows":
            crash_dir = self.findings / "default" / "crashes"
        return [f for f in crash_dir.iterdir() if f.is_file() and f.name != "README.txt"]
    
    def analyze_crash(self, crash_file, target):
        gdb_cmd = "gdb.exe" if platform.system() == "Windows" else "gdb"
        script = f"file {target}\nrun < {crash_file}\nbt\nquit"
        
        with open("gdb_script", "w") as f:
            f.write(script)
            
        try:
            proc = subprocess.run([gdb_cmd, "-batch", "-x", "gdb_script"], 
                                timeout=30, capture_output=True)
            signal = "UNKNOWN"
            if b"SIGSEGV" in proc.stdout or b"SIGSEGV" in proc.stderr:
                signal = "SIGSEGV"
            return {"status": "crash", "signal": signal}
        except:
            return {"status": "error"}
        finally:
            if os.path.exists("gdb_script"):
                os.unlink("gdb_script")
    
    def run_triage(self, target):
        crashes = self.get_crashes()
        for crash in crashes:
            res = self.analyze_crash(crash, target)
            self.results[str(crash)] = res
