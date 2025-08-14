import sqlite3
import json
import hashlib
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

class VulnLifecycle:
    def __init__(self, db_path="vulns.db"):
        self.db = db_path
        self.init_tables()
        
    def init_tables(self):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS vulns_lifecycle (
                    id TEXT PRIMARY KEY,
                    cve_id TEXT,
                    target TEXT,
                    type TEXT,
                    severity REAL,
                    status TEXT,
                    discovered_date TEXT,
                    triaged_date TEXT,
                    assigned_date TEXT,
                    patched_date TEXT,
                    verified_date TEXT,
                    closed_date TEXT,
                    owner TEXT,
                    patch_ver TEXT,
                    regression_test TEXT,
                    notes TEXT)''')
                    
        c.execute('''CREATE TABLE IF NOT EXISTS patch_analysis (
                    id TEXT,
                    patch_file BLOB,
                    diff_hash TEXT,
                    test_results TEXT,
                    regression_passed BOOLEAN,
                    created_date TEXT)''')
                    
        conn.commit()
        conn.close()
        
    def add_vuln(self, vuln_id, target, vuln_type, severity=0.0):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute("INSERT INTO vulns_lifecycle VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                 (vuln_id, None, target, vuln_type, severity, 'discovered',
                  datetime.now().isoformat(), None, None, None, None, None,
                  'unassigned', None, None, None))
        conn.commit()
        conn.close()
        
    def triage_vuln(self, vuln_id, severity, owner):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute("UPDATE vulns_lifecycle SET severity=?, status='triaged', triaged_date=?, owner=? WHERE id=?",
                 (severity, datetime.now().isoformat(), owner, vuln_id))
        conn.commit()
        conn.close()
        
    def assign_vuln(self, vuln_id, owner):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute("UPDATE vulns_lifecycle SET owner=?, status='assigned', assigned_date=? WHERE id=?",
                 (owner, datetime.now().isoformat(), vuln_id))
        conn.commit()
        conn.close()
        
    def get_metrics(self):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        
        metrics = {}
        c.execute("SELECT COUNT(*) FROM vulns_lifecycle WHERE status='discovered'")
        metrics['discovered'] = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM vulns_lifecycle WHERE status='triaged'")
        metrics['triaged'] = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM vulns_lifecycle WHERE status='patched'")
        metrics['patched'] = c.fetchone()[0]
        
        c.execute("SELECT AVG(julianday(patched_date) - julianday(discovered_date)) FROM vulns_lifecycle WHERE patched_date IS NOT NULL")
        avg_days = c.fetchone()[0] or 0
        metrics['avg_patch_days'] = avg_days
        
        conn.close()
        return metrics

class PatchDiff:
    def __init__(self, vuln_id):
        self.vuln_id = vuln_id
        
    def analyze_patch(self, old_binary, new_binary):
        # run diff on binaries
        cmd = ["diff", "-u", old_binary, new_binary]
        try:
            diff = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
            diff_hash = hashlib.sha256(diff.encode()).hexdigest()
            
            # store patch analysis
            conn = sqlite3.connect("vulns.db")
            c = conn.cursor()
            c.execute("INSERT INTO patch_analysis VALUES (?, ?, ?, ?, ?, ?)",
                     (self.vuln_id, diff.encode(), diff_hash, None, None, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            
            return diff_hash
        except subprocess.CalledProcessError:
            return None
            
    def extract_changes(self, diff_output):
        changes = []
        for line in diff_output.split('\n'):
            if line.startswith('+') and not line.startswith('+++'):
                changes.append(('added', line[1:]))
            elif line.startswith('-') and not line.startswith('---'):
                changes.append(('removed', line[1:]))
        return changes

class RegressionTest:
    def __init__(self, test_dir="tests"):
        self.test_dir = Path(test_dir)
        self.test_dir.mkdir(exist_ok=True)
        
    def create_test_case(self, vuln_id, crash_input):
        test_file = self.test_dir / f"test_{vuln_id}.py"
        
        test_content = f'''#!/usr/bin/env python3
import subprocess
import sys

def test_vuln_{vuln_id}():
    """Regression test for {vuln_id}"""
    crash_input = {repr(crash_input)}
    
    # run target with crash input
    proc = subprocess.Popen(['./harness'], 
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    
    stdout, stderr = proc.communicate(input=crash_input)
    
    # check if crash occurs
    if proc.returncode != 0:
        print("FAIL: Vulnerability still exists")
        return False
    else:
        print("PASS: Vulnerability patched")
        return True

if __name__ == "__main__":
    sys.exit(0 if test_vuln_{vuln_id}() else 1)
'''
        
        test_file.write_text(test_content)
        test_file.chmod(0o755)
        
    def run_regression(self, vuln_id):
        test_file = self.test_dir / f"test_{vuln_id}.py"
        if not test_file.exists():
            return None
            
        try:
            result = subprocess.run([sys.executable, str(test_file)], 
                                  capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False

class CVETracker:
    def __init__(self):
        self.api_url = "https://services.nvd.nist.gov/rest/json/cves/1.0"
        
    def search_cve(self, keyword, max_results=10):
        # mock CVE search - replace with real API
        mock_cves = [
            {"id": "CVE-2024-0001", "description": f"Buffer overflow in {keyword}", "cvss": 9.8},
            {"id": "CVE-2024-0002", "description": f"Use-after-free in {keyword}", "cvss": 8.1}
        ]
        return mock_cves[:max_results]
        
    def assign_cve(self, vuln_id, cve_id):
        conn = sqlite3.connect("vulns.db")
        c = conn.cursor()
        c.execute("UPDATE vulns_lifecycle SET cve_id=? WHERE id=?", (cve_id, vuln_id))
        conn.commit()
        conn.close()

class ExploitReliability:
    def __init__(self, vuln_id):
        self.vuln_id = vuln_id
        
    def test_reliability(self, exploit_path, target_path, iterations=100):
        successes = 0
        failures = 0
        
        for i in range(iterations):
            try:
                result = subprocess.run([exploit_path, target_path], 
                                      capture_output=True, timeout=10)
                if result.returncode == 0:
                    successes += 1
                else:
                    failures += 1
            except subprocess.TimeoutExpired:
                failures += 1
            except Exception:
                failures += 1
                
        reliability = (successes / iterations) * 100
        
        # store results
        conn = sqlite3.connect("vulns.db")
        c = conn.cursor()
        c.execute("UPDATE vulns_lifecycle SET notes=? WHERE id=?",
                 (f"Reliability: {reliability:.1f}%", self.vuln_id))
        conn.commit()
        conn.close()
        
        return reliability
        
    def generate_report(self, vuln_id):
        conn = sqlite3.connect("vulns.db")
        c = conn.cursor()
        
        c.execute("SELECT * FROM vulns_lifecycle WHERE id=?", (vuln_id,))
        vuln_data = c.fetchone()
        
        if not vuln_data:
            return None
            
        report = {
            'vuln_id': vuln_data[0],
            'cve_id': vuln_data[1],
            'target': vuln_data[2],
            'status': vuln_data[5],
            'discovered': vuln_data[6],
            'patched': vuln_data[9],
            'verified': vuln_data[10],
            'owner': vuln_data[12],
            'regression_passed': vuln_data[14]
        }
        
        conn.close()
        return report
