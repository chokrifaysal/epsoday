import os
import subprocess
import signal
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
quit
"""
        
        with open("/tmp/gdb_script", "w") as f:
            f.write(gdb_script)
            
        try:
            proc = subprocess.Popen(
                ["gdb", "-batch", "-x", "/tmp/gdb_script"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            try:
                stdout, stderr = proc.communicate(timeout=30)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.communicate()
                return {"status": "timeout", "signal": "SIGKILL"}
                
            signal = "UNKNOWN"
            if b"SIGSEGV" in stdout or b"SIGSEGV" in stderr:
                signal = "SIGSEGV"
            elif b"SIGABRT" in stdout or b"SIGABRT" in stderr:
                signal = "SIGABRT"
                
            return {"status": "crash", "signal": signal}
        except:
            return {"status": "error"}
    
    def run_triage(self, target):
        crashes = self.get_crashes()
        for crash in crashes:
            res = self.analyze_crash(crash, target)
            self.results[str(crash)] = res
            
            import sqlite3
            conn = sqlite3.connect("vulns.db", timeout=10)
            c = conn.cursor()
            try:
                c.execute("SELECT id FROM vulns WHERE crash_file=?", (str(crash),))
                if not c.fetchone():
                    vid = f"crash_{len(self.results)}"
                    c.execute("INSERT INTO vulns (id, target, type, status, desc, found_date, crash_file) VALUES (?, ?, ?, ?, ?, datetime('now'), ?)",
                             (vid, target, res["signal"], 'triage', res["status"], str(crash)))
                conn.commit()
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e):
                    time.sleep(0.1)
            finally:
                conn.close()
