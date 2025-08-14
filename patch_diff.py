#!/usr/bin/env python3
import difflib
import subprocess
import json
from pathlib import Path

class BinaryDiff:
    def __init__(self, old_bin, new_bin):
        self.old = old_bin
        self.new = new_bin
        
    def generate_asm_diff(self):
        """Generate assembly diff between binaries"""
        # disassemble both binaries
        old_asm = subprocess.check_output(["objdump", "-d", self.old], 
                                        text=True)
        new_asm = subprocess.check_output(["objdump", "-d", self.new], 
                                        text=True)
        
        # create diff
        diff = list(difflib.unified_diff(
            old_asm.splitlines(keepends=True),
            new_asm.splitlines(keepends=True),
            fromfile=self.old,
            tofile=self.new
        ))
        
        return ''.join(diff)
        
    def analyze_security_fix(self, diff_output):
        """Analyze diff for security fixes"""
        security_patterns = [
            'strcpy', 'strcat', 'sprintf', 'gets',
            'malloc', 'memcpy', 'strncpy'
        ]
        
        fixes = []
        for line in diff_output.split('\n'):
            if line.startswith('+') and any(p in line.lower() for p in security_patterns):
                fixes.append({
                    'type': 'security_fix',
                    'line': line[1:].strip(),
                    'pattern': [p for p in security_patterns if p in line.lower()][0]
                })
                
        return fixes
        
    def check_bounds_checks(self, diff_output):
        """Check if bounds checks were added"""
        bounds_patterns = [
            'if.*len',
            'if.*size',
            'if.*length',
            'cmp.*size',
            'test.*size'
        ]
        
        checks = []
        for line in diff_output.split('\n'):
            if line.startswith('+') and any(p in line.lower() for p in bounds_patterns):
                checks.append({
                    'type': 'bounds_check',
                    'line': line[1:].strip()
                })
                
        return checks

class VulnTrackingAPI:
    def __init__(self):
        self.base_url = "/api/v1"
        
    def get_vuln_status(self, vuln_id):
        conn = sqlite3.connect("vulns.db")
        c = conn.cursor()
        
        c.execute("SELECT * FROM vulns_lifecycle WHERE id=?", (vuln_id,))
        vuln = c.fetchone()
        
        if vuln:
            status = {
                'id': vuln[0],
                'cve_id': vuln[1],
                'status': vuln[5],
                'owner': vuln[12],
                'metrics': {
                    'days_to_patch': None,
                    'days_to_verify': None
                }
            }
            
            if vuln[6] and vuln[9]:
                discovered = datetime.fromisoformat(vuln[6])
                patched = datetime.fromisoformat(vuln[9])
                status['metrics']['days_to_patch'] = (patched - discovered).days
                
            return status
            
        return None
        
    def update_status(self, vuln_id, status, **kwargs):
        conn = sqlite3.connect("vulns.db")
        c = conn.cursor()
        
        fields = {
            'status': status,
            'owner': kwargs.get('owner'),
            'cve_id': kwargs.get('cve_id'),
            'notes': kwargs.get('notes')
        }
        
        for field, value in fields.items():
            if value is not None:
                c.execute(f"UPDATE vulns_lifecycle SET {field}=? WHERE id=?", 
                         (value, vuln_id))
                         
        conn.commit()
        conn.close()
