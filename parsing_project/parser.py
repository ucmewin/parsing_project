import re
from typing import List, Optional, Dict

def safe_float(val, field_name=""):
    try:
        return float(val)
    except Exception:
        print(f"Could not convert field '{field_name}' with value '{val}' to float.")
        return 0.0


line_item_pattern = re.compile(
    r"""^\s*(\d{3})\s+                # Line number
    ([^\s]+)\s+                       # Item code
    (.+?)\s{2,}                       # Description (non-greedy, ends at double space)
    ([\d.,-]+)\s+([A-Z%]+)\s+         # Units and UM
    ([\d.,-]+)\*?\s+([A-Z%]+)\s+      # Price and Price UM
    ([\d.,-]+)\s+([A-Z%]+)\s+         # Cost and Cost UM
    ([\d.,-]+)\s+                     # Extension
    ([\d\-.]+)%?\s+                   # GM%
    ([^\s]+)\s+                       # CLS
    ([YN])\s+([YN])\s+([YNU])\s+      # T, M, I
    ([^\s]+)\s+                       # R
    ([^\s]+)\s+                       # GL
    ([\d.,-]+)?%?\s*                  # COMM% (optional)
    ([A-Z0-9]*)?                      # SW (optional)
    $""", re.VERBOSE
)
def parse_line_item(line: str) -> Optional[Dict]:
    match = line_item_pattern.match(line)
    if not match:
        print(f"Could not parse line item: {line}")
        return None
    groups = match.groups()
    return {
        "ln#": int(groups[0]),
        "ITEM": groups[1],
        "Description": groups[2].strip(),
        "units": safe_float(groups[3], "units"),
        "UM": groups[4],
        "PRICE": safe_float(groups[5], "PRICE"),
        "PRICE_UM": groups[6],
        "COST": safe_float(groups[7], "COST"),
        "COST_UM": groups[8],
        "extension": safe_float(groups[9], "extension"),
        "gm%": groups[10],
        "CLS": groups[11],
        "T": groups[12],
        "M": groups[13],
        "I": groups[14],
        "R": groups[15],
        "GL": groups[16],
        "COMM%": groups[17] if groups[17] else "",
        "SW": groups[18] if groups[18] else "",
    }

def is_line_item(line: str) -> bool:
    # Must start at the very beginning (or after a few spaces) with 3 digits, then a space, then a non-space (item code)
    if not re.match(r'^\s{0,3}\d{3}\s+\S', line):
        return False
    # Must be at least 40 characters long (real line items are long)
    if len(line.strip()) < 40:
        return False
    # Exclude lines with known headers, dashes, or too many spaces
    if (
        "LN# ITEM" in line or
        "DESCRIPTION" in line or
        set(line.strip()) == {'-'} or
        line.strip() == ""
    ):
        return False
    return True

def parse_invoice_header(line: str) -> Optional[Dict]:
    try:
        cost_str = gm_str = tax_str = ""
        chunk = line[74:104]

        # Updated regex: handles 1-3 digit negatives with optional decimals
        match = re.search(r'(\d+\.\d{2})(-\d{1,3}(?:\.\d+)?)%?', chunk)
        if match:
            cost_str, gm_str = match.groups()
            tax_start = 74 + match.end()
            tax_str = line[tax_start:104].strip()
        else:
            cost_gm_field = line[74:92]
            if '-' in cost_gm_field and ' ' not in cost_gm_field:
                # Handles merged field like 15.00-999.9
                match = re.fullmatch(r'(\d+\.\d{2})(-\d{1,3}(?:\.\d+)?)', cost_gm_field)
                if match:
                    cost_str, gm_str = match.groups()
                    tax_start = 74 + match.end()
                    tax_str = line[tax_start:104].strip()
                else:
                    raise ValueError(f"Could not split cost/gm: {cost_gm_field}")
            else:
                cost_str = line[74:83].strip()
                gm_str = line[83:92].strip()
                tax_str = line[93:104].strip()

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
                "expected_subtotal": safe_float(line[59:70].strip(), "expected_subtotal"),
                "cost": safe_float(cost_str, "cost"),
                "gm_percent": gm_str,
                "tax": safe_float(tax_str, "tax"),
                "freight": safe_float(line[105:114].strip(), "freight"),
                "discount": safe_float(line[115:124].strip(), "discount"),
                "doc_total": safe_float(line[125:136].strip(), "doc_total"),
                "calculated_subtotal": 0.0,
                "match": False
            }
        }
    except Exception as e:
        print(f"⚠️ Error parsing header: {e}\n{line}")
        return None

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
