# lab4-seng471

This repository contains Python user and donation workflow modules.

## Included modules

- `user_management.py` — registration, verification, account update, admin approve/suspend/remove workflows.
- `cli.py` — command-line interface for user registration and management.
- `US-07.py`, `US-08.py`, `US-09.py` — existing donation and food need domain logic from main branch.

## Running tests

Install Python 3.10+ and run:

```bash
python -m unittest discover -s tests
```

## CLI usage

Run the command-line interface with:

```bash
python cli.py <command> [options]
```

Examples:

```bash
python cli.py register --name "Alice" --email alice@example.com --password securepass --role user
python cli.py register --name "Org" --email org@example.com --password securepass --role organization --organization-name "Good Org" --verification-docs https://example.com/doc.pdf
python cli.py list-users
python cli.py authenticate --email alice@example.com --password securepass
```
