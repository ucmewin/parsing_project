# parser.py

import re
from typing import List, Optional, Dict


def parse_invoice_header(line: str) -> Optional[Dict]:
    try:
        return {
            "invoice_number": line[0:6].strip(),
            "invoice_date": line[7:15].strip(),
            "term_code": line[16:18].strip().replace('*', ''),
            "over_credit_limit": '*' in line[16:18],
            "warehouse": line[20:22].strip(),
            "salesperson": line[23:26].strip(),
            "pick_ticket": line[27:39].strip(),
            "customer_code": line[40:49].strip(),
            "customer_name": line[50:58].strip(),
            "totals": {
                "expected_subtotal": float(line[59:70].strip()),
                "cost": float(line[74:83].strip()),
                "gm_percent": line[83:92].strip(),
                "tax": float(line[93:104].strip()),
                "freight": float(line[105:114].strip()),
                "discount": float(line[115:124].strip()),
                "doc_total": float(line[125:136].strip()),
                "calculated_subtotal": 0.0,
                "match": False
            }
        }
    except Exception as e:
        print(f"⚠️ Error parsing header: {e}\n{line}")
        return None


def parse_line_item(line: str) -> Optional[Dict]:
    try:
        if not re.match(r'^\s*\d{3}\s+\S', line):
            raise ValueError("Line doesn't start with a valid line number.")

        line_number_str = line[0:3].strip()
        if not line_number_str.isdigit():
            raise ValueError("Invalid or missing line number.")

        return {
            "ln#": int(line[0:3].strip()),
            "ITEM": line[4:24].strip(),
            "Description": line[25:49].strip(),
            "units": float(line[50:55].strip()),
            "UM": line[56:58].strip(),
            "PRICE": float(line[59:68].replace('*', '').strip()),
            "PRICE_OVERRIDE": '*' in line[68:69],
            "PRICE_UM": line[70:72].strip(),
            "COST": float(line[73:82].strip()),
            "COST_UM": line[83:85].strip(),
            "extension": float(line[86:96].strip()),
            "gm%": line[97:102].strip(),
            "CLS": line[104:107].strip(),
            "T": line[108:109].strip(),
            "M": line[110:111].strip(),
            "I": line[112:113].strip(),
            "R": line[114:115].strip(),
            "GL": line[116:119].strip(),
            "COMM%": line[120:124].strip(),
            "SW": line[127:129].strip()
        }
    except Exception as e:
        print(f"⚠️ Error parsing line item: {e}")
        return None


def is_line_item(line: str) -> bool:
    return bool(re.match(r'^\s*\d{3}\s+\S', line)) and not (
        line.strip().startswith("LN#") or
        line.strip().startswith("-") or
        "DESCRIPTION" in line
    )


def extract_invoices(text: str, target_customer=None, target_date=None, limit=None) -> List[Dict]:
    invoices = []
    lines = text.splitlines()
    i = 0
    current_invoice = None

    while i < len(lines):
        line = lines[i]

        if line.startswith(("DATE:", "USER:", "===")):
            i += 1
            continue

        if re.match(r'^\d{6} \d{2}/\d{2}/\d{2}', line):
            header = parse_invoice_header(line)
            if not header:
                i += 1
                continue

            if (target_customer and header["customer_code"] != target_customer) or \
               (target_date and header["invoice_date"] != target_date):
                current_invoice = None
                i += 1
                continue

            current_invoice = {**header, "items": []}
            invoices.append(current_invoice)
            i += 1

            # Skip separators or headers
            while i < len(lines) and (
                lines[i].strip().startswith("LN#") or
                lines[i].strip().startswith("-") or
                not lines[i].strip()
            ):
                i += 1

            while i < len(lines) and is_line_item(lines[i]):
                item = parse_line_item(lines[i])
                if item:
                    current_invoice["items"].append(item)
                i += 1

            if limit and len(invoices) >= limit:
                break

            continue

        if "Invoice #" in line and "(Continued)" in line:
            match = re.search(r'Invoice # (\d{6})', line)
            if match:
                inv_number = match.group(1)
                current_invoice = next((inv for inv in invoices if inv["invoice_number"] == inv_number), None)
            i += 1
            continue

        if current_invoice and is_line_item(line):
            item = parse_line_item(line)
            if item:
                current_invoice["items"].append(item)
            i += 1
            continue

        i += 1

    # Calculate totals
    for invoice in invoices:
        invoice["totals"]["calculated_subtotal"] = round(sum(item["extension"] for item in invoice["items"]), 2)
        invoice["totals"]["match"] = abs(invoice["totals"]["expected_subtotal"] - invoice["totals"]["calculated_subtotal"]) < 0.01

    return invoices
