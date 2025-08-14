#!/usr/bin/env python3
import sys
import argparse
from fuzz import runFuzz
from vuln import trackVuln, getVulns, initDB
from triage import Triage

# TODO: fix this import later
# from evasion import EDRBypass  # this was causing issues on linux

def main():
    ap = argparse.ArgumentParser(description='EPSODAY - zero-day research')
    ap.add_argument('-t', '--target', required=True, help='target binary')
    ap.add_argument('-f', '--fuzz', action='store_true', help='run fuzzing')
    ap.add_argument('-v', '--vuln', action='store_true', help='track vulns')
    ap.add_argument('--triage', action='store_true', help='triage crashes')
    ap.add_argument('--rust', action='store_true', help='use rust modules')  # broken rn
    
    args = ap.parse_args()
    
    if args.fuzz:
        # runFuzz(args.target)  # commented out for debugging
        print(f"would fuzz {args.target}")
    elif args.vuln:
        trackVuln(args.target)
    elif args.triage:
        initDB()
        tr = Triage("findings")
        tr.run_triage(args.target)
        print(f"Triaged crashes (hopefully)")
    else:
        print("need to specify something, idk what")

if __name__ == "__main__":
    main()#!/usr/bin/env python3

