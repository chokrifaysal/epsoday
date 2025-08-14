import os
import subprocess

def runFuzz(target):
    print(f"fuzzing {target}")
    # placeholder for AFL++ integration
    cmd = ["afl-fuzz", "-i", "in", "-o", "out", target]
    subprocess.run(cmd)
