import json
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials

from bot.config import BotConfig
from bot.constants import (
    TransactionType, COL_TYPE, COL_AMOUNT, COL_TOTAL,
    COL_DESCRIPTION, HEADERS, COL_LETTER_AMOUNT, COL_LETTER_TOTAL,
    NEW_SHEET_ROWS, NEW_SHEET_COLS
)


config = BotConfig.from_env()
_client = None
_spreadsheet = None
_current_sheet = None
_current_sheet_name = None


def get_client():
    global _client
    if _client is None:
        creds = Credentials.from_service_account_info(json.loads(config.google_creds), scopes=config.scopes)
        _client = gspread.authorize(creds)
    return _client


def get_spreadsheet():
    """Cache and return the opened spreadsheet doc"""
    global _spreadsheet
    if _spreadsheet is None:
        try:
            client = get_client()
            _spreadsheet = client.open(config.sheet_name)
        except Exception as e:
            print(f"Error opening spreadsheet: {e}")
            _spreadsheet = None
            raise

    return _spreadsheet


def get_monthly_sheet():
    """Cache and return the current month's worksheet"""
    global _current_sheet, _current_sheet_name, _spreadsheet
    month_name = datetime.now().strftime("%m-%Y")

    if _current_sheet is None or _current_sheet_name != month_name:
        try:
            doc = get_spreadsheet()
            _current_sheet = doc.worksheet(month_name)
        except gspread.exceptions.WorksheetNotFound:
            doc = get_spreadsheet()
            _current_sheet = doc.add_worksheet(title=month_name, rows=NEW_SHEET_ROWS, cols=NEW_SHEET_COLS)
            _current_sheet.append_row(HEADERS)
        except Exception:
            # Clear caches on connection/API error to force re-fetch next time
            if _spreadsheet is not None:
                _spreadsheet = None

            _current_sheet = None
            raise

        _current_sheet_name = month_name

    return _current_sheet


def get_records_from_previous_month() -> int:
    now = datetime.now()
    year, month = now.year, now.month

    if month == 1:
        month = 12
        year -= 1
    else:
        month -= 1

    prev_sheet_name = f"{month:02d}-{year}"
    try:
        doc = get_spreadsheet()
        prev_sheet = doc.worksheet(prev_sheet_name)
        return prev_sheet.get_all_records()
    except gspread.exceptions.WorksheetNotFound:
        return None
    except Exception:
        global _spreadsheet
        if _spreadsheet is not None:
            _spreadsheet = None

        raise


def get_last_total() -> int:
    sheet = get_monthly_sheet()
    records = sheet.get_all_records()
    if records:
        try:
            return int(records[-1][COL_TOTAL])
        except (ValueError, TypeError, KeyError):
            return 0
    else:
        previous_month_records = get_records_from_previous_month()
        if previous_month_records:
            try:
                return int(previous_month_records[-1][COL_TOTAL])
            except (ValueError, TypeError, KeyError):
                return 0

        return 0


def get_total() -> int:
    return get_last_total()


def add_transaction(amount, transaction_type, description=None) -> int:
    # Ensure amount is signed correctly (positive for income, negative for expense)
    amount = abs(amount) if transaction_type == TransactionType.INCOME else -abs(amount)

    sheet = get_monthly_sheet()
    all_values = sheet.get_all_values()
    next_row = len(all_values) + 1

    # Estimate previous total
    prev_total = 0
    if next_row == 2:
        # Carry over the final total from the previous month
        previous_month_records = get_records_from_previous_month()
        if previous_month_records:
            try:
                prev_total = int(previous_month_records[-1][COL_TOTAL])
            except (ValueError, TypeError, KeyError):
                prev_total = 0

        total_formula = f"={prev_total}+{COL_LETTER_AMOUNT}{next_row}"
    else:
        # Use sequential running total formula referencing the row above
        total_formula = f"={COL_LETTER_TOTAL}{next_row-1}+{COL_LETTER_AMOUNT}{next_row}"
        try:
            total_col_idx = HEADERS.index(COL_TOTAL)
            prev_total = int(all_values[-1][total_col_idx])
        except (ValueError, TypeError, IndexError):
            prev_total = 0

    sheet.append_row([
        transaction_type.value,
        amount,
        total_formula,
        description,
        datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    ], value_input_option="USER_ENTERED")

    return prev_total + amount


def get_expenses_stats(monthly_sheet_name: str) -> str:
    try:
        doc = get_spreadsheet()
        sheet = doc.worksheet(monthly_sheet_name)
        return "\n".join(
            f'💸 Расход: {abs(row[COL_AMOUNT]):<5} AZN | 💰 Остаток: {row[COL_TOTAL]:<5} AZN | 📌 {row[COL_DESCRIPTION] or "-"}'
            for row in sheet.get_all_records()
            if TransactionType(row[COL_TYPE]) == TransactionType.EXPENSE
        )
    except gspread.exceptions.WorksheetNotFound:
        return None
    except Exception:
        global _spreadsheet
        if _spreadsheet is not None:
            _spreadsheet = None

        raise
