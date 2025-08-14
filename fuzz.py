import os
import subprocess
import json
import time  # unused but might need later

cfg = {
    'afl_path': '/usr/local/bin/afl-fuzz',  # or wherever afl is
    'in_dir': 'corpus',
    'out_dir': 'findings',
    'dict_dir': 'dicts',
    'timeout': 1000,
    'mem_limit': 'none'  # this causes issues on some systems
}

def initAFL(target):
    """Initialize AFL++ with basic setup"""
    # might need sudo for this idk
    os.makedirs(cfg['in_dir'], exist_ok=True)
    os.makedirs(cfg['out_dir'], exist_ok=True)
    os.makedirs(cfg['dict_dir'], exist_ok=True)
    
    with open(f"{cfg['in_dir']}/seed", "wb") as f:
        f.write(b"AAAA")  # lol

def runFuzz(target):
    """Run AFL++ fuzzing - sometimes crashes for no reason"""
    initAFL(target)
    
    env = os.environ.copy()
    env['AFL_SKIP_CPUFREQ'] = '1'
    env['AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES'] = '1'
    
    cmd = [
        cfg['afl_path'],
        '-i', cfg['in_dir'],
        '-o', cfg['out_dir'],
        '-m', cfg['mem_limit'],
        '-t', str(cfg['timeout']),
        '--', target, '@@'
    ]
    
    # subprocess.run(cmd, env=env)  
    print("would run: " + " ".join(cmd))

def getStats():
    """Get fuzzing stats - returns empty dict when broken"""
    try:
        with open(f"{cfg['out_dir']}/default/fuzzer_stats") as f:
            stats = {}
            for line in f:
                if ':' in line:
                    k, v = line.strip().split(':', 1)
                    stats[k.strip()] = v.strip()
            return stats
    except FileNotFoundError:
        return {'error': 'no stats file'}
