# utils.py

import os
import re
import logging
from pathlib import Path
from datetime import datetime

# Configure root logger
def setup_logging(verbose=False, logfile=None):
    level = logging.DEBUG if verbose else logging.INFO
    handlers = [logging.StreamHandler()]
    if logfile:
        handlers.append(logging.FileHandler(logfile, mode='a', encoding='utf-8'))

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

def log(message, level="info"):
    getattr(logging, level.lower(), logging.info)(message)

def format_date(raw_date):
    """Convert MM/DD/YY to YYYY-MM-DD"""
    try:
        return datetime.strptime(raw_date, "%m/%d/%y").strftime("%Y-%m-%d")
    except Exception:
        return raw_date  # fallback

def sanitize_filename(name):
    """Remove unsafe characters for filenames"""
    return re.sub(r'[^a-zA-Z0-9._-]', '_', name)

def ensure_within_directory(base_path, target_path):
    """Ensure path stays within the expected base directory"""
    base = Path(base_path).resolve()
    target = Path(target_path).resolve()
    return str(target).startswith(str(base))

def is_valid_invoice_number(value):
    return bool(re.fullmatch(r'\d{6}', value))

def is_valid_date(value):
    try:
        datetime.strptime(value, "%m/%d/%y")
        return True
    except ValueError:
        return False
def get_output_folder(base, date=None, customer=None):
    if date:
        return Path(base) / "by_date" / format_date(date)
    if customer:
        return Path(base) / "by_customer" / sanitize_filename(customer)
    return Path(base) / format_date(datetime.today().strftime("%m/%d/%y"))
