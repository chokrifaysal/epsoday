#!/usr/bin/env python3
import os
import subprocess
import platform
import shutil

def install_deps():
    system = platform.system()
    
    if system == "Windows":
        print("Installing on Windows...")
        subprocess.run(["pip", "install", "-r", "requirements.txt"])
        
    elif system == "Linux":
        print("Installing on Linux...")
        subprocess.run(["sudo", "apt", "update"])
        subprocess.run(["sudo", "apt", "install", "-y", 
                       "build-essential", "afl++", "python3-pip", "gdb"])
        subprocess.run(["pip3", "install", "-r", "requirements.txt"])
        
    elif system == "Darwin":
        print("Installing on macOS...")
        subprocess.run(["brew", "install", "afl-fuzz", "python3"])
        subprocess.run(["pip3", "install", "-r", "requirements.txt"])
        
    print("Building Rust...")
    subprocess.run(["cargo", "build", "--release"], cwd="rust_exploit")
    
    print("Building C...")
    subprocess.run(["make"])

if __name__ == "__main__":
    install_deps()
    print("EPSODAY ready")
