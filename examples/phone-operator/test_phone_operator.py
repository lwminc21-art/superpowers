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
from phone_operator import Caller, normalize_phone, run


class NormalizePhoneTests(unittest.TestCase):
    def test_accepts_formatted_numbers(self):
        self.assertEqual(normalize_phone("(555) 123-4567"), "5551234567")
        self.assertEqual(normalize_phone("555.0100"), "5550100")

    def test_rejects_too_short_or_non_numeric(self):
        self.assertIsNone(normalize_phone("123"))
        self.assertIsNone(normalize_phone("not a phone"))


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

    def test_schedule_appointment_is_persisted(self):
        caller = Caller(script=[
            "1", "Jane Doe", "555-123-4567", "Tuesday 10am", "Checkup", "0",
        ])
        run(caller)
        records = json.loads(po.APPOINTMENTS_FILE.read_text())
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "Jane Doe")
        self.assertEqual(records[0]["phone"], "5551234567")
        self.assertEqual(records[0]["type"], "appointment")

    def test_take_message_is_persisted(self):
        caller = Caller(script=[
            "2", "John Smith", "(555) 987 6543", "Send lab results.", "0",
        ])
        run(caller)
        records = json.loads(po.MESSAGES_FILE.read_text())
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["message"], "Send lab results.")

    def test_invalid_inputs_are_reprompted(self):
        caller = Caller(script=[
            "9",            # invalid menu choice
            "2", "",        # empty name -> reprompt
            "Pat Lee", "abc",  # bad phone -> reprompt
            "555-0100", "Call me back", "0",
        ])
        run(caller)
        records = json.loads(po.MESSAGES_FILE.read_text())
        self.assertEqual(records[0]["name"], "Pat Lee")
        self.assertEqual(records[0]["phone"], "5550100")


if __name__ == "__main__":
    unittest.main()
