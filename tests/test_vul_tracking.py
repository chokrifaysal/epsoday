#!/usr/bin/env python3
import pytest
import tempfile
import json
from vuln import addVuln, getVulns, initDB

class TestVulnTracking:
    def setup_method(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.temp_db.name
        
    def teardown_method(self):
        os.unlink(self.db_path)
        
    def test_add_vulnerability(self):
        vuln_id = addVuln("test_target", "buffer_overflow", "heap overflow", "crash.bin")
        assert len(vuln_id) == 8
        
    def test_get_vulnerabilities(self):
        addVuln("target1", "type1", "desc1", "crash1")
        addVuln("target2", "type2", "desc2", "crash2")
        
        vulns = getVulns()
        assert len(vulns) >= 2
        
    def test_filter_by_target(self):
        addVuln("specific_target", "type", "desc", "crash")
        
        vulns = getVulns("specific_target")
        assert len(vulns) == 1
        assert vulns[0][1] == "specific_target"
