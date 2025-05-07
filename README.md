# 🧾 Daily Sales Register Parser

This tool parses fixed-width daily sales register text files exported from ERP systems like **Infor FACTS**, extracting invoice data and converting it into structured **JSON** and **CSV** formats.

---

## 📂 Folder Structure

```
parsing_project/
├── main.py                 # Entry point
├── parser.py              # Invoice and line item parsing logic
├── file_ops.py            # File reading, JSON/CSV output, file movement
├── utils.py               # Logging, formatting, validation
├── config.py              # Central config values
├── dailysalesreg/         # Input folder for .txt files
│   └── logged/            # Processed files moved here
├── json_output/
│   ├── by_date/YYYY-MM-DD/
│   ├── customers/CUSTOMER_CODE/
│   └── invoice_number.json
└── processed_files.log    # Hashes of processed files to prevent duplicates
```

---

## 🚀 Getting Started

### Requirements

- Python 3.7+
- No external packages required (uses standard library)

---

## ▶️ Usage

### Basic (Parse all `.txt` files in `dailysalesreg/`)
```bash
python main.py
```

### Parse single file
```bash
python main.py dailysalesreg/05022025.txt
```

### Filter by customer
```bash
python main.py --customer 1766
```

### Filter by invoice date
```bash
python main.py --date 05/02/25
```

---

## ⚙️ Options

| Argument           | Description                                              |
|--------------------|----------------------------------------------------------|
| `file`             | (optional) Path to a `.txt` file to parse                |
| `--customer`       | Only extract invoices for a customer code                |
| `--date`           | Only extract invoices for a date (format: MM/DD/YY)      |
| `--limit`          | Process only first N invoices (for testing)              |
| `--dry-run`        | Don’t save JSON/CSV or move files                        |
| `--skip-move`      | Don’t move processed `.txt` file to `logged/` folder     |
| `--skip-processed` | Force reprocessing even if file was already handled      |
| `--verbose`        | Enable debug logging in console                          |
| `--logfile name`   | Write logs to a specific file (default: `process.log`)   |

---

## 📦 Output

- JSON files are saved per invoice.
- A summary CSV with totals and match-check is generated per run.
- Files are organized under `json_output/` by:
  - Full runs → `json_output/by_date/YYYY-MM-DD/`
  - Customer runs → `json_output/customers/1766/`
  - Date runs → `json_output/dates/YYYY-MM-DD/`

---

## ✅ Features

- Line item and header parsing
- Handles continued invoice pages
- Validates totals vs. calculated extensions
- Logs errors, skips bad lines, shows matches
- Supports CLI filtering, logging, testing
- Safe file handling and duplicate protection

---

## 📌 Notes

- Invoice number must be 6 digits.
- Dates must be in MM/DD/YY format.
- Only `.txt` files placed in `dailysalesreg/` will be picked up automatically.

---

## 🛠 Example Development Command

```bash
python main.py --customer 100000 --verbose --dry-run --limit 5
```

---

## 🧑‍💻 Author

Kyle Allen  
Levocraft
[Levocraft]

---
