#!/usr/bin/env python3
"""Tests for the virtual phone operator.

Run with: python3 test_phone_operator.py
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import phone_operator as po
from phone_operator import Caller, load_crm, normalize_phone, run

# A caller phone number that is NOT in any CRM.
UNKNOWN_PHONE = "555-123-4567"
# A practice from the bundled crm.csv (GOOD NEIGHBOR CLINIC FOUNDATION).
CRM_PHONE = "323-298-1668"


class NormalizePhoneTests(unittest.TestCase):
    def test_accepts_formatted_numbers(self):
        self.assertEqual(normalize_phone("(555) 123-4567"), "5551234567")
        self.assertEqual(normalize_phone("555.0100"), "5550100")

    def test_rejects_too_short_or_non_numeric(self):
        self.assertIsNone(normalize_phone("123"))
        self.assertIsNone(normalize_phone("not a phone"))


class CrmTests(unittest.TestCase):
    def test_bundled_crm_loads_and_is_indexed_by_phone(self):
        crm = load_crm()
        self.assertGreater(len(crm), 0, "crm.csv should contain prospects")
        record = crm.get(normalize_phone(CRM_PHONE))
        self.assertIsNotNone(record, "GOOD NEIGHBOR CLINIC should be reachable")
        self.assertEqual(record["name"], "GOOD NEIGHBOR CLINIC FOUNDATION")

    def test_missing_crm_file_yields_empty_index(self):
        self.assertEqual(load_crm(Path("/nonexistent/crm.csv")), {})


class CallFlowTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        data_dir = Path(self._tmp.name)
        self._patches = [
            mock.patch.object(po, "DATA_DIR", data_dir),
            mock.patch.object(po, "APPOINTMENTS_FILE", data_dir / "appointments.json"),
            mock.patch.object(po, "MESSAGES_FILE", data_dir / "messages.json"),
        ]
        for p in self._patches:
            p.start()

    def tearDown(self):
        for p in self._patches:
            p.stop()
        self._tmp.cleanup()

    def test_unknown_caller_is_asked_for_a_name(self):
        caller = Caller(script=[
            "1", UNKNOWN_PHONE, "Jane Doe", "Tuesday 10am", "Checkup", "0",
        ])
        run(caller, crm={})
        records = json.loads(po.APPOINTMENTS_FILE.read_text())
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "Jane Doe")
        self.assertEqual(records[0]["phone"], "5551234567")
        self.assertNotIn("crm_npi", records[0])

    def test_known_caller_is_recognized_from_crm(self):
        crm = {
            "5551112222": {
                "name": "GOOD NEIGHBOR CLINIC FOUNDATION",
                "city": "Los Angeles",
                "specialty": "Family/Geriatric",
                "npi": "1043162076",
            }
        }
        caller = Caller(script=[
            "1", "(555) 111-2222", "Wednesday 2pm", "RPM enrollment", "0",
        ])
        run(caller, crm=crm)
        records = json.loads(po.APPOINTMENTS_FILE.read_text())
        self.assertEqual(records[0]["name"], "GOOD NEIGHBOR CLINIC FOUNDATION")
        self.assertEqual(records[0]["crm_npi"], "1043162076")
        self.assertTrue(
            any("GOOD NEIGHBOR CLINIC" in line for line in caller.transcript),
            "operator should greet a recognized caller by name",
        )

    def test_take_message_is_persisted(self):
        caller = Caller(script=[
            "2", UNKNOWN_PHONE, "John Smith", "Send lab results.", "0",
        ])
        run(caller, crm={})
        records = json.loads(po.MESSAGES_FILE.read_text())
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["message"], "Send lab results.")

    def test_invalid_inputs_are_reprompted(self):
        caller = Caller(script=[
            "9",                 # invalid menu choice
            "2", "abc",          # bad phone -> reprompt
            "555-0100", "",      # empty name -> reprompt
            "Pat Lee", "Call me back", "0",
        ])
        run(caller, crm={})
        records = json.loads(po.MESSAGES_FILE.read_text())
        self.assertEqual(records[0]["name"], "Pat Lee")
        self.assertEqual(records[0]["phone"], "5550100")


if __name__ == "__main__":
    unittest.main()
