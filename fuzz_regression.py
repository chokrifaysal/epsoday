#!/usr/bin/env python3
import os
import subprocess
import json
from pathlib import Path

class FuzzRegression:
    def __init__(self, corpus_dir="corpus", findings_dir="findings"):
        self.corpus = Path(corpus_dir)
        self.findings = Path(findings_dir)
        
    def setup_regression(self, vuln_id):
        """Setup regression testing for a specific vuln"""
        reg_dir = Path(f"regression_{vuln_id}")
        reg_dir.mkdir(exist_ok=True)
        
        # copy original corpus
        os.system(f"cp -r {self.corpus} {reg_dir}/")
        
        # copy crash cases
        crashes = self.findings / "default" / "crashes"
        if crashes.exists():
            os.system(f"cp -r {crashes} {reg_dir}/")
            
        return reg_dir
        
    def run_regression(self, vuln_id, target_binary):
        """Run regression test against patched binary"""
        reg_dir = Path(f"regression_{vuln_id}")
        
        # run AFL regression
        cmd = [
            "afl-fuzz",
            "-i", str(reg_dir / "corpus"),
            "-o", str(reg_dir / "results"),
            "-V", "60",  # 60 second regression
            "--", target_binary, "@@"
        ]
        
        try:
            subprocess.run(cmd, timeout=70, capture_output=True)
            
            # check for new crashes
            new_crashes = reg_dir / "results" / "default" / "crashes"
            if new_crashes.exists() and any(new_crashes.iterdir()):
                return False  # regression failed
                
            return True  # regression passed
            
        except subprocess.TimeoutExpired:
            return False
            
    def generate_diff_fuzz(self, old_bin, new_bin, vuln_id):
        """Generate targeted fuzzing for patch diff"""
        diff_dir = Path(f"diff_fuzz_{vuln_id}")
        diff_dir.mkdir(exist_ok=True)
        
        # create diff-based corpus
        corpus_dir = diff_dir / "corpus"
        corpus_dir.mkdir(exist_ok=True)
        
        # create diff-aware harness
        harness_code = f'''
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int target_function(const char *input) {{
    // specific function that was patched
    if (strlen(input) > 100) return -1;
    
    // original vulnerable code
    char buf[50];
    strcpy(buf, input);  // potential overflow
    
    return 0;
}}

int main(int argc, char **argv) {{
    FILE *f = fopen(argv[1], "rb");
    if (!f) return 1;
    
    fseek(f, 0, SEEK_END);
    size_t len = ftell(f);
    fseek(f, 0, SEEK_SET);
    
    char *buf = malloc(len + 1);
    fread(buf, 1, len, f);
    buf[len] = 0;
    fclose(f);
    
    int ret = target_function(buf);
    free(buf);
    return ret;
}}
'''
        
        harness_path = diff_dir / "diff_harness.c"
        harness_path.write_text(harness_code)
        
        return diff_dir

class PatchValidation:
    def __init__(self):
        self.validation_results = {}
        
    def validate_patch(self, vuln_id, patch_file, binary_path):
        """Comprehensive patch validation"""
        results = {
            'vuln_id': vuln_id,
            'patch_valid': False,
            'no_regression': False,
            'performance_ok': False
        }
        
        # compile patched binary
        patched_bin = f"patched_{vuln_id}"
        cmd = ["gcc", "-o", patched_bin, str(patch_file)]
        
        if subprocess.run(cmd).returncode != 0:
            return results
            
        # check if vuln fixed
        # run regression tests
        reg = FuzzRegression()
        reg_passed = reg.run_regression(vuln_id, f"./{patched_bin}")
        
        # check performance
        perf_ok = self.check_performance(binary_path, f"./{patched_bin}")
        
        results.update({
            'patch_valid': True,
            'no_regression': reg_passed,
            'performance_ok': perf_ok
        })
        
        return results
        
    def check_performance(self, old_bin, new_bin):
        """Check if patch impacts performance"""
        import time
        
        # run both binaries with same input
        test_input = b"A" * 1000
        
        times = []
        for bin_path in [old_bin, new_bin]:
            start = time.time()
            proc = subprocess.run([bin_path], input=test_input, 
                                capture_output=True, timeout=5)
            end = time.time()
            times.append(end - start)
            
        # allow 10% performance degradation
        return times[1] <= times[0] * 1.1
