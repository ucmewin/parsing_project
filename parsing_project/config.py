# config.py

from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "dailysalesreg"
LOGGED_DIR = INPUT_DIR / "logged"
OUTPUT_DIR = BASE_DIR / "json_output"
CUSTOMER_OUTPUT_DIR = OUTPUT_DIR / "customers"
DATE_OUTPUT_DIR = OUTPUT_DIR / "dates"

# Log files
LOGFILE_DEFAULT = BASE_DIR / "process.log"
SKIPPED_LOG = BASE_DIR / "skipped.log"

# CSV summary filename
CSV_SUMMARY_FILENAME = "invoice_summary.csv"
