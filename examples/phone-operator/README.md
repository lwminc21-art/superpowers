# Virtual Phone Operator

A zero-dependency, text-based IVR (interactive voice response) simulation. The
operator greets callers and lets them **schedule an appointment** or **leave a
message**. Both are saved to JSON so a human can review them later.

## Usage

```sh
python3 phone_operator.py
```

You'll get a menu:

```
How can I help you today?
  1. Schedule an appointment
  2. Leave a message
  3. Hear these options again
  0. End the call
```

- **Schedule an appointment** — collects name, callback number, preferred
  day/time, and reason for the visit.
- **Leave a message** — collects name, callback number, and the message.

Empty answers and invalid phone numbers are re-prompted automatically.

## Where records go

Records are appended to JSON files in `data/` next to the script:

- `data/appointments.json`
- `data/messages.json`

The `data/` directory is git-ignored.

## Tests

```sh
python3 test_phone_operator.py
```

## Customizing

Edit the `BUSINESS_NAME` and `HOURS` constants at the top of
`phone_operator.py` to fit your organization.
