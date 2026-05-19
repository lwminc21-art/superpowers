#!/usr/bin/env python3
"""Virtual phone operator (IVR).

A zero-dependency, text-based interactive voice response simulation. It greets
callers, then lets them schedule an appointment or leave a message. Both are
persisted to JSON files so a human can review them later.

Run interactively:

    python3 operator.py

Records are written to the ``data/`` directory next to this script.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
APPOINTMENTS_FILE = DATA_DIR / "appointments.json"
MESSAGES_FILE = DATA_DIR / "messages.json"

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


def normalize_phone(raw: str) -> str | None:
    """Return digits of a plausible phone number, or None if it is not one."""
    digits = re.sub(r"\D", "", raw)
    if 7 <= len(digits) <= 15:
        return digits
    return None


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


def schedule_appointment(caller: Caller) -> None:
    caller.say("\nLet's get you on the schedule.")
    record = {
        "type": "appointment",
        "name": prompt_required(caller, "Your full name: "),
        "phone": prompt_phone(caller, "A callback number: "),
        "preferred_time": prompt_required(
            caller, f"Preferred day and time ({HOURS}): "
        ),
        "reason": prompt_required(caller, "Briefly, the reason for your visit: "),
        "received_at": datetime.now().isoformat(timespec="seconds"),
    }
    save_record(APPOINTMENTS_FILE, record)
    caller.say(
        f"\nThank you, {record['name']}. Your appointment request for "
        f"\"{record['preferred_time']}\" has been logged. "
        "Our staff will call to confirm."
    )


def take_message(caller: Caller) -> None:
    caller.say("\nI'll take a message for our staff.")
    record = {
        "type": "message",
        "name": prompt_required(caller, "Your full name: "),
        "phone": prompt_phone(caller, "A callback number: "),
        "message": prompt_required(caller, "Your message: "),
        "received_at": datetime.now().isoformat(timespec="seconds"),
    }
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


def run(caller: Caller) -> None:
    caller.say(f"Thank you for calling {BUSINESS_NAME}. Our hours are {HOURS}.")
    caller.say(MENU)
    while True:
        choice = caller.ask("Enter 1, 2, 3, or 0: ")
        if choice == "1":
            schedule_appointment(caller)
            caller.say(MENU)
        elif choice == "2":
            take_message(caller)
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
