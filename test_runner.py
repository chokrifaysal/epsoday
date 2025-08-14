#!/usr/bin/env python3
import subprocess
import time
import json
import os
from pathlib import Path

class TestRunner:
    def __init__(self, target_dir="targets"):
        self.target_dir = Path(target_dir)
        self.results = []
        
    def compile_target(self, source_path):
        bin_path = source_path.with_suffix('')
        cmd = ["gcc", "-o", str(bin_path), str(source_path), "-fsanitize=address"]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return bin_path
        except subprocess.CalledProcessError as e:
            return None
            
    def test_exploit_reliability(self, exploit_path, target_path, iterations=50):
        successes = 0
        for i in range(iterations):
            try:
                proc = subprocess.run([exploit_path, target_path], 
                                    timeout=5, capture_output=True)
                if proc.returncode == 0:
                    successes += 1
            except:
                pass
                
        return (successes / iterations) * 100
        
    def run_regression(self, test_cases):
        results = []
        for case in test_cases:
            bin_path = self.compile_target(case['source'])
            if not bin_path:
                results.append({'test': case['name'], 'status': 'compile_fail'})
                continue
                
            reliability = self.test_exploit_reliability(case['exploit'], bin_path)
            results.append({
                'test': case['name'],
                'status': 'pass' if reliability > 80 else 'fail',
                'reliability': reliability
            })
            
        return results

class CIBuilder:
    def __init__(self):
        self.build_status = {}
        
    def build_rust(self):
        os.chdir("rust_exploit")
        result = subprocess.run(["cargo", "build", "--release"], 
                              capture_output=True)
        os.chdir("..")
        return result.returncode == 0
        
    def build_c(self):
        result = subprocess.run(["make", "clean"], capture_output=True)
        result = subprocess.run(["make"], capture_output=True)
        return result.returncode == 0
        
    def build_all(self):
        self.build_status['rust'] = self.build_rust()
        self.build_status['c'] = self.build_c()
        return self.build_status
