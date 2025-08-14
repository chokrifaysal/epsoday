import sqlite3
import json
import uuid
from datetime import datetime

def initDB():
    db = sqlite3.connect("vulns.db")
    c = db.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS vulns 
                 (id TEXT PRIMARY KEY, target TEXT, type TEXT, status TEXT, 
                  desc TEXT, found_date TEXT, crash_file TEXT, exploitability TEXT)''')
    db.commit()
    db.close()

def addVuln(target, type, desc, crash_file, exploitability="unknown"):
    db = sqlite3.connect("vulns.db")
    c = db.cursor()
    vid = str(uuid.uuid4())[:8]
    c.execute("INSERT INTO vulns VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (vid, target, type, 'new', desc, datetime.now().isoformat(), crash_file, exploitability))
    db.commit()
    db.close()
    return vid

def getVulns(target=None):
    db = sqlite3.connect("vulns.db")
    c = db.cursor()
    if target:
        c.execute("SELECT * FROM vulns WHERE target=?", (target,))
    else:
        c.execute("SELECT * FROM vulns")
    return c.fetchall()

def updateVuln(vid, status, exploitability=None):
    db = sqlite3.connect("vulns.db")
    c = db.cursor()
    if exploitability:
        c.execute("UPDATE vulns SET status=?, exploitability=? WHERE id=?", (status, exploitability, vid))
    else:
        c.execute("UPDATE vulns SET status=? WHERE id=?", (status, vid))
    db.commit()
    db.close()
