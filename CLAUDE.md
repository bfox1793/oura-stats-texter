# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**oura-stats-texter** automatically fetches Oura Ring health data and sends a daily text message summary to a user. It integrates with the Oura Ring API and an SMS provider (likely Twilio).

## Project Status

This project is in early development — only scaffolding (README, LICENSE, .gitignore) exists. No source code, dependencies, or configuration files have been added yet.

## Expected Architecture

When implemented, the project will likely need:
- **Oura API client** — fetch daily health stats (sleep, readiness, activity scores)
- **SMS sender** — deliver formatted stats via text message (e.g., Twilio)
- **Scheduler** — trigger daily at a configured time (cron or cloud scheduler)
- **Config/secrets** — API tokens and phone numbers via environment variables (`.env` excluded from git per `.gitignore`)

## Development Setup

This is a Python project. Expected setup pattern (update this once dependencies are defined):

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # or: pip install -e .
```

Environment variables will be needed (create a `.env` file — it is gitignored):
- Oura API personal access token
- SMS provider credentials (e.g., Twilio account SID, auth token, phone numbers)

## Tooling

The `.gitignore` is configured for:
- `pytest` — testing
- `mypy` — type checking
- `ruff` — linting/formatting

Once configured, typical commands will be:
```bash
pytest                  # run tests
pytest tests/test_foo.py::test_name  # run single test
mypy .                  # type check
ruff check .            # lint
ruff format .           # format
```
