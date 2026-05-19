# Virtual Phone Operator

A zero-dependency, text-based IVR (interactive voice response) simulation. The
operator greets callers, **recognizes them from a CRM call sheet** by their
phone number, and lets them **schedule an appointment** or **leave a message**.
Both are saved to JSON so a human can review them later.

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

- **Schedule an appointment** — collects callback number, preferred day/time,
  and reason for the visit.
- **Leave a message** — collects callback number and the message.

After the caller gives a callback number, the operator looks it up in the CRM:

- **Recognized** — the caller is greeted by practice name (e.g. "I see you're
  calling from GOOD NEIGHBOR CLINIC FOUNDATION in Los Angeles") and that name
  is used for the record, along with the practice's NPI (`crm_npi`).
- **Not recognized** — the caller is asked for their name as a new contact.

Empty answers and invalid phone numbers are re-prompted automatically.

## CRM call sheet (`crm.csv`)

`crm.csv` is the **Prospects** tab of the CCM/RPM prospect workbook, exported to
CSV (the rest of the workbook — dashboard, playbook, instructions — is not
needed by the operator). It is indexed by the `Phone` column; the operator also
reads `Practice / Provider`, `City`, `Specialty`, and `NPI`.

To refresh it, re-export the Prospects tab as CSV with the same header row and
replace `crm.csv`. A missing `crm.csv` simply disables recognition — every
caller is then treated as new.

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
