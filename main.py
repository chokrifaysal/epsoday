#!/usr/bin/env python3
import sys
import argparse
from fuzz import runFuzz
from vuln import trackVuln, getVulns, initDB
from triage import Triage
from evasion import EDRBypass, SleepObfuscation, StackSpoofing

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-t', '--target', required=True)
    ap.add_argument('-f', '--fuzz', action='store_true')
    ap.add_argument('-v', '--vuln', action='store_true')
    ap.add_argument('--triage', action='store_true')
    ap.add_argument('--evasion', action='store_true')
    
    args = ap.parse_args()
    
    if args.fuzz:
        runFuzz(args.target)
    elif args.vuln:
        trackVuln(args.target)
    elif args.triage:
        initDB()
        tr = Triage("findings")
        tr.run_triage(args.target)
        print(f"Triaged {len(tr.results)} crashes")
    elif args.evasion:
        print("evasion toolkit loaded")
        # TODO: implement evasion chain
    else:
        print("specify -f, -v, --triage, or --evasion")

if __name__ == "__main__":
    main()
