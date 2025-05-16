# parsing/main.py

import argparse
import os
from pathlib import Path

from parsing_project.parser import extract_invoices
from parsing_project.file_ops import (
    read_text_file,
    save_json,
    save_csv_summary,
    move_file_to_logged,
    has_been_processed,
    record_processed,
)
from parsing_project.utils import (
    format_date,
    sanitize_filename,
    setup_logging,
    log,
    get_output_folder,
)

DEFAULT_INPUT_FOLDER = "dailysalesreg"
LOGGED_FOLDER = os.path.join(DEFAULT_INPUT_FOLDER, "logged")
PROCESSED_LOG = "processed_files.log"


def process_file(file_path, args):
    text = read_text_file(file_path)

    invoices = extract_invoices(
        text,
        target_customer=args.customer,
        target_date=args.date,
        limit=args.limit
    )

    if not invoices:
        log(f"❌ No matching invoices found in {file_path}.", "warning")
        return False

    # Determine output subfolder
    if args.customer:
        folder = get_output_folder("json_output/customers", args.customer)
    elif args.date:
        folder = get_output_folder("json_output/dates", args.date)
    else:
        invoice_date = invoices[0]["invoice_date"]
        folder = get_output_folder("json_output", invoice_date)

    # File output (skip if dry run)
    if not args.dry_run:
        save_json(invoices, folder)
        save_csv_summary(invoices, folder / "invoice_summary.csv")

    # Only move file if it was fully processed
    if not (args.customer or args.date) and not args.dry_run and not args.skip_move:
        record_processed(file_path, PROCESSED_LOG)
        move_file_to_logged(file_path, LOGGED_FOLDER)


def process_all_files(args):
    folder = Path(DEFAULT_INPUT_FOLDER)
    files = list(folder.glob("*.txt"))

    if not files:
        log("📂 No .txt files found in dailysalesreg/", "warning")
        return

    for file in files:
        if not (args.customer or args.date) and args.skip_processed and has_been_processed(file, PROCESSED_LOG):
            log(f"⚠️ Skipping already processed file: {file.name}", "debug")
            continue
        process_file(file, args)


def main():
    parser = argparse.ArgumentParser(description="Parse daily sales register invoices.")
    parser.add_argument("file", nargs="?", help="Path to .txt file, or omit to process all")
    parser.add_argument("--customer", help="Filter by customer code")
    parser.add_argument("--date", help="Filter by invoice date (MM/DD/YY)")
    parser.add_argument("--dry-run", action="store_true", help="Parse without writing output")
    parser.add_argument("--skip-move", action="store_true", help="Don't move .txt to logged/")
    parser.add_argument("--skip-processed", action="store_true", help="Don't reprocess known files")
    parser.add_argument("--limit", type=int, help="Limit number of invoices processed")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    parser.add_argument("--logfile", default="process.log", help="Log output file name")

    args = parser.parse_args()
    setup_logging(verbose=args.verbose, logfile=args.logfile)

    if args.file:
        path = Path(args.file)
        if not path.exists():
            log(f"❌ File not found: {args.file}", "error")
            return
        process_file(path, args)
    else:
        process_all_files(args)


if __name__ == "__main__":
    main()
