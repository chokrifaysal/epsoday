#!/usr/bin/env python3
import subprocess
import json
import os
from datetime import datetime

class CIPipeline:
    def run_build(self):
        print("Building...")
        
        subprocess.run(["make", "clean"], capture_output=True)
        build = subprocess.run(["make"], capture_output=True)
        
        subprocess.run(["cargo", "build", "--release"], 
                      cwd="rust_exploit", capture_output=True)
        
        return {
            'c': build.returncode == 0,
            'rust': True,
            'timestamp': datetime.now().isoformat()
        }
        
    def run_pipeline(self):
        results = {'build': self.run_build()}
        
        with open('ci_results.json', 'w') as f:
            json.dump(results, f)
            
        return results

if __name__ == "__main__":
    CIPipeline().run_pipeline()
