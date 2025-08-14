import os
import json
import subprocess
from pathlib import Path

def walk_crashes(findings_dir, target):
    crash_dir = Path(findings_dir) / "default" / "crashes"
    if not crash_dir.exists():
        return
        
    results = {}
    for crash in crash_dir.iterdir():
        if crash.is_file() and crash.name != "README.txt":
            # run exploitable
            gdb_script = f"""
set pagination off
file {target}
run < {crash}
source gdb_exploitable.py
exploitable
quit
"""
            with open("/tmp/exploit_check", "w") as f:
                f.write(gdb_script)
                
            try:
                out = subprocess.check_output(["gdb", "-batch", "-x", "/tmp/exploit_check"], 
                                            stderr=subprocess.STDOUT, text=True, timeout=10)
                results[str(crash)] = out
            except:
                results[str(crash)] = "timeout"
                
    with open("crash_analysis.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    import sys
    walk_crashes(sys.argv[1], sys.argv[2])
