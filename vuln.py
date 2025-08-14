import sqlite3
import json

def trackVuln(target):
    print(f"tracking vulns in {target}")
    db = sqlite3.connect("vulns.db")
    c = db.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS vulns (id TEXT, target TEXT, type TEXT, status TEXT)")
    db.commit()
    db.close()
