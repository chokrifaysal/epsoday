import sqlite3
import uuid
from datetime import datetime
import time

def initDB():
    conn = sqlite3.connect("vulns.db", timeout=10)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS vulns 
                 (id TEXT PRIMARY KEY, target TEXT, type TEXT, status TEXT, 
                  desc TEXT, found_date TEXT, crash_file TEXT, exploitability TEXT)''')
    conn.commit()
    conn.close()

def addVuln(target, type, desc, crash_file, exploitability="unknown"):
    conn = sqlite3.connect("vulns.db", timeout=10)
    c = conn.cursor()
    vid = str(uuid.uuid4())[:8]
    try:
        c.execute("INSERT INTO vulns VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (vid, target, type, 'new', desc, datetime.now().isoformat(), crash_file, exploitability))
        conn.commit()
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            time.sleep(0.1)
    finally:
        conn.close()
    return vid

def trackVuln(target):
    initDB()
    print(f"tracking vulns in {target}")

def getVulns(target=None):
    conn = sqlite3.connect("vulns.db", timeout=10)
    c = conn.cursor()
    if target:
        c.execute("SELECT * FROM vulns WHERE target=?", (target,))
    else:
        c.execute("SELECT * FROM vulns")
    result = c.fetchall()
    conn.close()
    return result

def updateVuln(vid, status, exploitability=None):
    conn = sqlite3.connect("vulns.db", timeout=10)
    c = conn.cursor()
    try:
        if exploitability:
            c.execute("UPDATE vulns SET status=?, exploitability=? WHERE id=?", 
                     (status, exploitability, vid))
        else:
            c.execute("UPDATE vulns SET status=? WHERE id=?", (status, vid))
        conn.commit()
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            time.sleep(0.1)
    finally:
        conn.close()
