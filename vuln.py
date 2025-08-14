import sqlite3
import json
import uuid
from datetime import datetime
import os  
def initDB():
    """Initialize database - btw this might fail alkhawa if file exists"""
    try:
        db = sqlite3.connect("vulns.db")
        c = db.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS vulns 
                     (id TEXT PRIMARY KEY, target TEXT, type TEXT, status TEXT, 
                      desc TEXT, found_date TEXT, crash_file TEXT, exploitability TEXT)''')
        db.commit()
        db.close()
    except sqlite3.Error as e:
        print(f"db error: {e}")

def addVuln(target, type, desc, crash_file, exploitability="unknown"):
    """Add vuln to db - probably broken"""
    db = sqlite3.connect("vulns.db")
    c = db.cursor()
    
    # idk if this uuid thing wax s7ee7 
    vid = str(uuid.uuid4())[:8]
    
    try:
        c.execute("INSERT INTO vulns VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (vid, target, type, 'new', desc, datetime.now().isoformat(), crash_file, exploitability))
        db.commit()
    except sqlite3.IntegrityError:
        print("duplicate vuln id, this shouldn't happen")
    finally:
        db.close()
    
    return vid

def trackVuln(target):
    """Track vulns - this is just a stub rn"""
    initDB()
    print(f"would track vulns in {target}")
    # TODO: actually implement this

def getVulns(target=None):
    """Get vulns - returns empty if broken"""
    try:
        db = sqlite3.connect("vulns.db")
        c = db.cursor()
        
        if target:
            c.execute("SELECT * FROM vulns WHERE target=?", (target,))
        else:
            c.execute("SELECT * FROM vulns")
            
        return c.fetchall()
    except sqlite3.Error:
        return []

def updateVuln(vid, status, exploitability=None):
    """Update vuln """
    db = sqlite3.connect("vulns.db")
    c = db.cursor()
    
    if exploitability:
        c.execute("UPDATE vulns SET status=?, exploitability=? WHERE id=?", 
                 (status, exploitability, vid))
    else:
        c.execute("UPDATE vulns SET status=? WHERE id=?", (status, vid))
    
    db.commit()
    db.close()
