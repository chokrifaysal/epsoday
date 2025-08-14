import os
import subprocess
import json

cfg = {
    'afl_path': '/usr/local/bin/afl-fuzz',
    'in_dir': 'corpus',
    'out_dir': 'findings',
    'dict_dir': 'dicts',
    'timeout': 1000,
    'mem_limit': 'none'
}

def initAFL(target):
    os.makedirs(cfg['in_dir'], exist_ok=True)
    os.makedirs(cfg['out_dir'], exist_ok=True)
    os.makedirs(cfg['dict_dir'], exist_ok=True)
    
    # basic seed
    with open(f"{cfg['in_dir']}/seed", "wb") as f:
        f.write(b"AAAA")

def runFuzz(target):
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
    
    subprocess.run(cmd, env=env)

def getStats():
    try:
        with open(f"{cfg['out_dir']}/default/fuzzer_stats") as f:
            return dict(line.strip().split(':', 1) for line in f if ':' in line)
    except:
        return {}
