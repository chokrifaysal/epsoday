#!/usr/bin/env python3
import sys
from rust_integration import RustIntegration

def test_rust():
    print("Testing Rust integration...")
    
    rust = RustIntegration()
    
    # test version
    ver = rust.get_version()
    print(f"Rust version: {ver}")
    
    # test arch
    arch = rust.check_arch()
    print(f"Architecture: {arch}-bit")
    
    # test encoding
    data = b"test payload"
    encoded = rust.encode_with_rust(data, 0x42)
    print(f"Original: {data}")
    print(f"Encoded: {encoded}")
    
    if rust.lib:
        print("Rust integration working")
        return True
    else:
        print("Rust lib not found - run 'cargo build --release' first")
        return False

if __name__ == "__main__":
    success = test_rust()
    sys.exit(0 if success else 1)
