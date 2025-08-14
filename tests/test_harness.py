#!/usr/bin/env python3
import pytest
import subprocess
import tempfile
import os
from pathlib import Path

def test_harness_compilation():
    """Test if harness compiles"""
    result = subprocess.run(["make"], capture_output=True)
    assert result.returncode == 0
    
def test_harness_execution():
    """Test basic harness execution"""
    harness_path = Path("./harness")
    assert harness_path.exists()
    
    # Create test input
    with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
        f.write(b"test input")
        temp_file = f.name
        
    result = subprocess.run([str(harness_path), temp_file], 
                          capture_output=True)
    os.unlink(temp_file)
    
    assert result.returncode == 0
    
def test_harness_crash():
    """Test harness with crash input"""
    harness_path = Path("./harness")
    
    # Create crash input
    with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
        f.write(b"FUZZ" + b"A" * 100)
        temp_file = f.name
        
    result = subprocess.run([str(harness_path), temp_file], 
                          capture_output=True)
    os.unlink(temp_file)
    
    # Should crash with ASAN
    assert result.returncode != 0
