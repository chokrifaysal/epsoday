#!/usr/bin/env python3
import sys
import argparse
from fuzz import runFuzz
from vuln import trackVuln

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-t', '--target', required=True)
    ap.add_argument('-f', '--fuzz', action='store_true')
    ap.add_argument('-v', '--vuln', action='store_true')
    
    args = ap.parse_args()
    
    if args.fuzz:
        runFuzz(args.target)
    elif args.vuln:
        trackVuln(args.target)
    else:
        print("specify -f or -v")

if __name__ == "__main__":
    main()
