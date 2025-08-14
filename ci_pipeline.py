#!/usr/bin/env python3
import subprocess
import json
import os
from datetime import datetime

class CIPipeline:
    def __init__(self):
        self.stages = ['build', 'test', 'package', 'deploy']
        self.results = {}
        
    def run_build(self):
        print("Building components...")
        
        # Build Rust modules
        rust_result = subprocess.run(
            ["cargo", "build", "--release"], 
            cwd="rust_exploit",
            capture_output=True
        )
        
        # Build C harness
        c_result = subprocess.run(["make", "clean"], capture_output=True)
        c_result = subprocess.run(["make"], capture_output=True)
        
        return {
            'rust': rust_result.returncode == 0,
            'c': c_result.returncode == 0,
            'timestamp': datetime.now().isoformat()
        }
        
    def run_tests(self):
        print("Running test suite...")
        
        # Unit tests
        unit_tests = subprocess.run(
            ["python3", "-m", "pytest", "tests/"], 
            capture_output=True
        )
        
        # Integration tests
        integration_tests = subprocess.run(
            ["python3", "test_runner.py"], 
            capture_output=True
        )
        
        return {
            'unit': unit_tests.returncode == 0,
            'integration': integration_tests.returncode == 0,
            'timestamp': datetime.now().isoformat()
        }
        
    def package_artifacts(self):
        print("Packaging artifacts...")
        
        package_dir = f"dist/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(package_dir, exist_ok=True)
        
        # Copy built files
        subprocess.run(["cp", "-r", "rust_exploit/target/release", f"{package_dir}/"])
        subprocess.run(["cp", "harness", f"{package_dir}/"])
        subprocess.run(["cp", "-r", "config", f"{package_dir}/"])
        
        return {'package_path': package_dir}
        
    def run_pipeline(self):
        print("Starting CI pipeline...")
        
        self.results['build'] = self.run_build()
        self.results['test'] = self.run_tests()
        self.results['package'] = self.package_artifacts()
        
        with open('ci_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
            
        return self.results
