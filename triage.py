import os
import subprocess
from pathlib import Path

class Triage:
    def __init__(self, findings_dir):
        self.findings = findings_dir
        self.results = {}
        
    def get_crashes(self):
        crash_dir = Path(self.findings) / "default" / "crashes"
        if not crash_dir.exists():
            return []
        return [f for f in crash_dir.iterdir() if f.is_file() and f.name != "README.txt"]
    
    def analyze_crash(self, crash_file, target):
        gdb_script = f"""
set pagination off
set logging file /tmp/gdb_{crash_file.name}.log
set logging on
file {target}
run < {crash_file}
bt
info registers
x/20x $sp
quit
"""
        
        with open("/tmp/gdb_script", "w") as f:
            f.write(gdb_script)
            
        try:
            subprocess.run(["gdb", "-batch", "-x", "/tmp/gdb_script"], 
                         timeout=30, capture_output=True, text=True)
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "signal": "SIGKILL"}
            
        try:
            with open(f"/tmp/gdb_{crash_file.name}.log") as f:
                log = f.read()
                
            signal = "UNKNOWN"
            if "SIGSEGV" in log:
                signal = "SIGSEGV"
            elif "SIGABRT" in log:
                signal = "SIGABRT"
                
            return {"status": "crash", "signal": signal, "log": log}
        except:
            return {"status": "error"}
    
    def run_triage(self, target):
        crashes = self.get_crashes()
        for crash in crashes:
            res = self.analyze_crash(crash, target)
            self.results[str(crash)] = res
            
            import sqlite3
            db = sqlite3.connect("vulns.db")
            c = db.cursor()
            c.execute("SELECT id FROM vulns WHERE crash_file=?", (str(crash),))
            if not c.fetchone():
                vid = f"crash_{len(self.results)}"
                c.execute("INSERT INTO vulns (id, target, type, status, desc, found_date, crash_file) VALUES (?, ?, ?, ?, ?, datetime('now'), ?)",
                         (vid, target, res["signal"], 'triage', res["status"], str(crash)))
            db.commit()
            db.close()
