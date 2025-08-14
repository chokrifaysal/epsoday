#!/usr/bin/env python3
import sys
import argparse
import os
from fuzz import runFuzz
from vuln import trackVuln, initDB
from triage import Triage

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-t', '--target', required=True)
    ap.add_argument('-f', '--fuzz', action='store_true')
    ap.add_argument('-v', '--vuln', action='store_true')
    ap.add_argument('--triage', action='store_true')
    ap.add_argument('--rust', action='store_true')
    
    args = ap.parse_args()
    
    if not os.path.exists(args.target):
        print(f"{args.target} not found")
        sys.exit(1)
        
    if args.fuzz:
        runFuzz(args.target)
    elif args.vuln:
        trackVuln(args.target)
    elif args.triage:
        initDB()
        tr = Triage("findings")
        tr.run_triage(args.target)
    elif args.rust:
        from rust_integration import RustIntegration
        rust = RustIntegration()
        print(f"Rust version: {rust.get_version()}")
        print(f"Architecture: {rust.check_arch()}-bit")
    else:
        print("specify -f, -v, --triage, or --rust")

if __name__ == "__main__":
    main()
