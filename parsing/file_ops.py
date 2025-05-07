# parsing/file_ops.py

import os
import csv
import json
import shutil
import hashlib
from pathlib import Path

from parsing.utils import format_date, sanitize_filename, log


def read_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()


def save_json(invoices, folder):
    os.makedirs(folder, exist_ok=True)
    for invoice in invoices:
        filename = sanitize_filename(f"{invoice['invoice_number']}.json")
        path = Path(folder) / filename
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(invoice, f, indent=2)
        log(f"✅ Saved JSON: {filename}", "debug")


def save_csv_summary(invoices, output_path):
    os.makedirs(output_path.parent, exist_ok=True)
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "Invoice #", "Date", "Customer Code", "Customer Name",
            "Subtotal", "Calculated", "Match?", "# Items", "Salesperson", "Doc Total"
        ])
        for inv in invoices:
            writer.writerow([
                inv["invoice_number"],
                inv["invoice_date"],
                inv["customer_code"],
                inv["customer_name"],
                inv["totals"]["expected_subtotal"],
                inv["totals"]["calculated_subtotal"],
                inv["totals"]["match"],
                len(inv["items"]),
                inv["salesperson"],
                inv["totals"]["doc_total"]
            ])
    log(f"📄 CSV summary saved to: {output_path}", "info")


def move_file_to_logged(file_path, logged_dir):
    os.makedirs(logged_dir, exist_ok=True)
    filename = os.path.basename(file_path)
    dest = os.path.join(logged_dir, filename)
    shutil.move(file_path, dest)
    log(f"📁 Moved to logged/: {filename}", "info")


def has_been_processed(file_path, processed_log):
    file_hash = hashlib.md5(Path(file_path).read_bytes()).hexdigest()
    if not os.path.exists(processed_log):
        return False

    with open(processed_log, 'r') as f:
        return file_hash in f.read()


def record_processed(file_path, processed_log):
    file_hash = hashlib.md5(Path(file_path).read_bytes()).hexdigest()
    with open(processed_log, 'a') as f:
        f.write(file_hash + "\n")
