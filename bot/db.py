import json
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials

from bot.config import BotConfig
from bot.constants import TransactionType

config = BotConfig.from_env()
creds = Credentials.from_service_account_info(json.loads(config.google_creds), scopes=config.scopes)
client = gspread.authorize(creds)


def get_monthly_sheet():
    month_name = datetime.now().strftime("%m-%Y")
    try:
        sheet = client.open(config.sheet_name).worksheet(month_name)
    except gspread.exceptions.WorksheetNotFound:
        sheet = client.open(config.sheet_name).add_worksheet(title=month_name, rows="1000", cols="10")
        sheet.append_row(["type", "amount", "total", "description", "created_at"])

    return sheet


def get_last_total_from_previous_month() -> int:
    now = datetime.now()
    year, month = now.year, now.month

    if month == 1:
        month = 12
        year -= 1
    else:
        month -= 1

    prev_sheet_name = f"{month:02d}-{year}"
    try:
        prev_sheet = client.open(config.sheet_name).worksheet(prev_sheet_name)
        records = prev_sheet.get_all_records()
        if records:
            return records[-1]["total"]
    except gspread.exceptions.WorksheetNotFound:
        return 0

    return 0


def get_last_total() -> int:
    sheet = get_monthly_sheet()
    records = sheet.get_all_records()
    if records:
        return records[-1]["total"]
    else:
        return get_last_total_from_previous_month()


def add_transaction(amount, transaction_type, description=None) -> int:
    amount = abs(amount) if transaction_type == TransactionType.INCOME else -abs(amount)
    prev_total = get_last_total()
    new_total = prev_total + amount

    sheet = get_monthly_sheet()
    sheet.append_row([
        transaction_type.value, amount, new_total, description,
        datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    ], value_input_option="USER_ENTERED")

    return new_total


def get_total() -> int:
    return get_last_total()
