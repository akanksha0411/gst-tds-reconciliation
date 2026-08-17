import pandas as pd
import numpy as np
import random
import string
from datetime import date, timedelta

# random.seed(69)
# np.random.seed(69)

N_VENDORS = 20
STATE_CODES = ["07", "27", "29", "33", "06", "24", "09", "19"]
fy_start = date(2025, 4, 1)
fy_end = date(2026, 3, 31)

def make_gstin(state_code: str) -> str:
    "Builds a usable GSTIN code, using the state_code(2) + PAN number (10) + entity(1) + taxpayer-type(Z) + checksum(1)"
    # PAN format -> ABCDE1234F (uppercase_alphabets(5) + digits(4) + uppercase_alphabets(1)) = 10
    create_pan = "".join(random.choices(string.ascii_uppercase, k=5)) + "".join(random.choices(string.digits, k=4)) + random.choice(string.ascii_uppercase)
    entity = random.choice(string.ascii_uppercase + string.digits)
    checksum = random.choice(string.ascii_uppercase + string.digits)
    return f"{state_code}{create_pan}{entity}Z{checksum}"

def create_vendors(n_vendors: int) -> pd.DataFrame:
    assert n_vendors <=20, "N_VENDORS more than vendor_name_prefixes, can't create vendor list"
    vendor_name_prefixes = [
    "Shree", "Om", "Global", "National", "Prime", "Apex", "Sun", "Metro",
    "United", "Bharat", "Silver", "Royal", "Classic", "Elite", "Modern",
    "Capital", "Prestige", "Horizon", "Vertex", "Pioneer"]

    vendor_name_suffixes = [
        "Enterprises", "Traders", "Industries", "Suppliers", "Corp",
        "Textiles", "Electricals", "Logistics", "Chemicals", "Distributors"]

    random.shuffle(vendor_name_prefixes)
    vendors = []
    unique_gstin = set()
    for i in range(n_vendors):
        name = f"{vendor_name_prefixes[i]} {random.choice(vendor_name_suffixes)}"
        gstin = make_gstin(random.choice(STATE_CODES))
        while True:
            if gstin not in unique_gstin:
                vendors.append({
                    "vendor_id" : f"V{i+1:03d}",
                    "vendor_name" : name,
                    "vendor_gstin" : gstin
                })
                unique_gstin.add(gstin)
                break
            gstin = make_gstin(random.choice(STATE_CODES))
    df = pd.DataFrame(vendors)
    return df

def random_invoice_dates(fy_start: date, fy_end: date) -> date:
    days_ = (fy_end - fy_start).days
    return fy_start + timedelta(days = random.randint(0, days_))


def create_invoices(vendors: pd.Series, low, high) -> pd.DataFrame:
    invoices = []
    invoice_cnt = 1
    buyer_state_code = "07"
    for i in vendors:
        vendor_gstin = i
        for j in range(random.randint(low, high)):
            invoice_id = f"INV{invoice_cnt:05d}"
            invoice_date = random_invoice_dates(fy_start, fy_end)
            filing_period = f"{invoice_date.month:02d}-{invoice_date.year}"
            invoice_number = f"INV/{invoice_date.month:02d}{invoice_date.year}/{j+1:05d}"
            amt_before_tax = round(random.uniform(2000, 250000), 2)
            gst_rate = random.choice([0.05, 0.12, 0.18, 0.28])
            state_code = vendor_gstin[:2]
            if state_code == buyer_state_code:
                cgst = round(amt_before_tax * gst_rate / 2, 2)
                sgst = round(amt_before_tax * gst_rate / 2, 2)
                igst = 0.0
            else:
                cgst = 0.0
                sgst = 0.0
                igst = round(amt_before_tax * gst_rate, 2)
            total_tax = round(cgst + sgst + igst, 2)
            total_invoice_value = round(amt_before_tax + total_tax, 2)
            invoices.append({
                "invoice_id" : invoice_id,
                "vendor_gstin" : vendor_gstin,
                "invoice_number" : invoice_number,
                "invoice_date" : invoice_date.isoformat(),
                "filing_period" : filing_period,
                "taxable_value" : amt_before_tax,
                "cgst" : cgst,
                "sgst" : sgst,
                "igst" : igst,
                "total_tax" : total_tax,
                "total_invoice_value" : total_invoice_value
            })
            invoice_cnt += 1
    df = pd.DataFrame(invoices)
    return df

if __name__ == "__main__":
    vendors = create_vendors(N_VENDORS)
    print(create_invoices(vendors["vendor_gstin"], 40, 60))