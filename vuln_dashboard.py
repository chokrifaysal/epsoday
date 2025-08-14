#!/usr/bin/env python3
import json
import sqlite3
from datetime import datetime, timedelta

class VulnDashboard:
    def __init__(self):
        self.db = "vulns.db"
        
    def generate_report(self):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        
        # overall metrics
        c.execute("SELECT COUNT(*) FROM vulns_lifecycle")
        total = c.fetchone()[0]
        
        c.execute("SELECT status, COUNT(*) FROM vulns_lifecycle GROUP BY status")
        status_counts = dict(c.fetchall())
        
        # weekly metrics
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        c.execute("SELECT COUNT(*) FROM vulns_lifecycle WHERE discovered_date > ?", (week_ago,))
        weekly_new = c.fetchone()[0]
        
        # critical vulns
        c.execute("SELECT COUNT(*) FROM vulns_lifecycle WHERE severity >= 8.0")
        critical = c.fetchone()[0]
        
        # average patch time
        c.execute("SELECT AVG(julianday(patched_date) - julianday(discovered_date)) FROM vulns_lifecycle WHERE patched_date IS NOT NULL")
        avg_patch = c.fetchone()[0] or 0
        
        report = {
            "generated": datetime.now().isoformat(),
            "total_vulns": total,
            "status_breakdown": status_counts,
            "weekly_new": weekly_new,
            "critical_vulns": critical,
            "avg_patch_days": round(avg_patch, 2)
        }
        
        conn.close()
        return report
        
    def export_json(self, filename="vuln_report.json"):
        report = self.generate_report()
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
