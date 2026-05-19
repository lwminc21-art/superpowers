#!/usr/bin/env python3
"""Virtual phone operator (IVR).

A zero-dependency, text-based interactive voice response simulation. It greets
callers, identifies them against a CRM call sheet, then lets them schedule an
appointment or leave a message. Both are persisted to JSON files so a human can
review them later.

Run interactively:

    python3 phone_operator.py

Records are written to the ``data/`` directory next to this script. Caller
identification reads ``crm.csv`` (the CCM/RPM prospect call sheet) next to this
script.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
APPOINTMENTS_FILE = DATA_DIR / "appointments.json"
MESSAGES_FILE = DATA_DIR / "messages.json"
CRM_FILE = HERE / "crm.csv"

BUSINESS_NAME = "Northside Family Clinic"
HOURS = "Monday to Friday, 9am to 5pm"


@dataclass
class Caller:
    """A line of communication to and from the caller.

    ``script`` lets tests drive the operator without real stdin; when it is
    exhausted (or None) input falls back to the keyboard.
    """

    script: list[str] | None = None
    transcript: list[str] = field(default_factory=list)

    def say(self, text: str) -> None:
        self.transcript.append(text)
        print(text)

    def ask(self, prompt: str) -> str:
        if self.script:
            answer = self.script.pop(0)
            self.transcript.append(f"{prompt}{answer}")
            return answer.strip()
        return input(prompt).strip()


def normalize_phone(raw: str) -> str | None:
    """Return digits of a plausible phone number, or None if it is not one."""
    digits = re.sub(r"\D", "", raw)
    if 7 <= len(digits) <= 15:
        return digits
    return None


def load_crm(path: Path = CRM_FILE) -> dict[str, dict]:
    """Index the CRM call sheet by normalized phone number.

    The CSV is the CCM/RPM prospect sheet exported from the workbook; only the
    fields the operator needs to recognize a caller are kept.
    """
    index: dict[str, dict] = {}
    if not path.exists():
        return index
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            phone = normalize_phone(row.get("Phone", ""))
            if not phone:
                continue
            index[phone] = {
                "name": row.get("Practice / Provider", "").strip(),
                "city": row.get("City", "").strip(),
                "specialty": row.get("Specialty", "").strip(),
                "npi": row.get("NPI", "").strip(),
            }
    return index


def load_records(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return []


def save_record(path: Path, record: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    records = load_records(path)
    records.append(record)
    path.write_text(json.dumps(records, indent=2))


def prompt_required(caller: Caller, question: str) -> str:
    """Ask until the caller gives a non-empty answer."""
    while True:
        answer = caller.ask(question)
        if answer:
            return answer
        caller.say("Sorry, I didn't catch that. Please try again.")


def prompt_phone(caller: Caller, question: str) -> str:
    while True:
        answer = caller.ask(question)
        phone = normalize_phone(answer)
        if phone:
            return phone
        caller.say("That doesn't look like a valid phone number. Please try again.")


def identify_caller(caller: Caller, crm: dict[str, dict]) -> dict:
    """Collect the callback number and match it against the CRM call sheet.

    Returns ``{"phone", "name", "crm_match"}``. On a CRM hit the caller is
    greeted by practice name and that name is reused; otherwise the caller is
    asked for their name as a new contact.
    """
    phone = prompt_phone(caller, "Your callback number: ")
    match = crm.get(phone)
    if match:
        where = f" in {match['city']}" if match["city"] else ""
        caller.say(f"Thanks — I see you're calling from {match['name']}{where}.")
        return {"phone": phone, "name": match["name"], "crm_match": match}
    return {
        "phone": phone,
        "name": prompt_required(caller, "Your full name: "),
        "crm_match": None,
    }


def schedule_appointment(caller: Caller, crm: dict[str, dict]) -> None:
    caller.say("\nLet's get you on the schedule.")
    ident = identify_caller(caller, crm)
    record = {
        "type": "appointment",
        "name": ident["name"],
        "phone": ident["phone"],
        "preferred_time": prompt_required(
            caller, f"Preferred day and time ({HOURS}): "
        ),
        "reason": prompt_required(caller, "Briefly, the reason for your visit: "),
        "received_at": datetime.now().isoformat(timespec="seconds"),
    }
    if ident["crm_match"]:
        record["crm_npi"] = ident["crm_match"]["npi"]
    save_record(APPOINTMENTS_FILE, record)
    caller.say(
        f"\nThank you, {record['name']}. Your appointment request for "
        f"\"{record['preferred_time']}\" has been logged. "
        "Our staff will call to confirm."
    )


def take_message(caller: Caller, crm: dict[str, dict]) -> None:
    caller.say("\nI'll take a message for our staff.")
    ident = identify_caller(caller, crm)
    record = {
        "type": "message",
        "name": ident["name"],
        "phone": ident["phone"],
        "message": prompt_required(caller, "Your message: "),
        "received_at": datetime.now().isoformat(timespec="seconds"),
    }
    if ident["crm_match"]:
        record["crm_npi"] = ident["crm_match"]["npi"]
    save_record(MESSAGES_FILE, record)
    caller.say(
        f"\nGot it, {record['name']}. Your message has been recorded and "
        "someone will get back to you."
    )


MENU = (
    "\nHow can I help you today?\n"
    "  1. Schedule an appointment\n"
    "  2. Leave a message\n"
    "  3. Hear these options again\n"
    "  0. End the call"
)


def run(caller: Caller, crm: dict[str, dict] | None = None) -> None:
    if crm is None:
        crm = load_crm()
    caller.say(f"Thank you for calling {BUSINESS_NAME}. Our hours are {HOURS}.")
    caller.say(MENU)
    while True:
        choice = caller.ask("Enter 1, 2, 3, or 0: ")
        if choice == "1":
            schedule_appointment(caller, crm)
            caller.say(MENU)
        elif choice == "2":
            take_message(caller, crm)
            caller.say(MENU)
        elif choice == "3":
            caller.say(MENU)
        elif choice == "0":
            caller.say("\nThank you for calling. Goodbye!")
            return
        else:
            caller.say("Sorry, that isn't a valid option.")


def main() -> int:
    caller = Caller()
    try:
        run(caller)
    except (EOFError, KeyboardInterrupt):
        caller.say("\nCall ended. Goodbye!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
