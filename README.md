# utilities_bot

A small, purpose-built Telegram bot for tracking a shared cash **treasury** (казна) —
recording income and expenses and keeping a running balance for a group that manages
communal funds (e.g. commandants at a residence). It is intentionally task-oriented,
not a general-purpose finance app. All UI text is in Russian; amounts are in AZN.

## How it works

- **Data lives in a Google Sheet**, one worksheet per month (`MM-YYYY`). This is
  deliberate: it's free, users can open/download the data themselves at any time, and
  the records survive even if the hosting server is lost.
- **Runs as a Flask webhook** (not long polling), deployed on the free tier of
  **PythonAnywhere**. `main.py:application` is the WSGI entrypoint; Telegram delivers
  each update as a POST to `/webhook`.
- **Two roles** (configured per Telegram user id): `editor` can add income/expenses;
  `reader` can only view the current total.

## Features

- 💰 View the current treasury total (carried over across months)
- 💵 Add income / 💸 add expense (with description), with running-balance formulas
- 📊 Monthly statistics (current / previous / custom month) filtered by income,
  expense, or all, with summary totals

## Project layout

| Path | Responsibility |
|------|----------------|
| `main.py` | Flask app + `/webhook` entrypoint (verifies Telegram secret, feeds updates to aiogram) |
| `bot/main.py` | Builds the aiogram `Dispatcher` and registers routers |
| `bot/config.py` | `BotConfig` — all env-driven configuration |
| `bot/constants.py` | Constants, keyboards, and user/role helpers |
| `bot/storage.py` | `SQLiteStorage` — file-backed FSM state (survives process restarts) |
| `bot/db.py` | Google Sheets data layer (via `gspread`) |
| `bot/handlers/` | One handler class per feature (start, income, expense, statistics, …) |
| `bot/states/` | FSM state groups for multi-step flows |

## Setup

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
# create a .env (see below), then run locally:
.venv/bin/flask --app main run
```

To receive messages, register your bot's webhook with Telegram so it points at the
public `/webhook` URL, using the same secret as `WEBHOOK_SECRET`.

## Configuration (`.env`)

| Variable | Description |
|----------|-------------|
| `BOT_TOKEN` | Telegram bot token |
| `GOOGLE_CREDS` | Google service-account credentials as a JSON string |
| `SHEET_NAME` | Name of the Google Spreadsheet to open |
| `WEBHOOK_URL` | Public webhook URL |
| `WEBHOOK_SECRET` | Shared secret validated on every webhook request |
| `ALLOWED_USERS` | JSON mapping `user_id → {"username", "role"}` (`editor`/`reader`) |
| `FSM_DB_PATH` | *(optional)* path to the SQLite file for conversation state; defaults to `database.sqlite3` in the project root |
| `http_proxy` / `https_proxy` | *(optional)* proxy for outbound Telegram calls (needed on PythonAnywhere free tier) |
