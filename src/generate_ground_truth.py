import pandas as pd
import numpy as np
import random
import string
from datetime import date, timedelta

random.seed(69)
np.random.seed(69)

N_VENDORS = 20
STATE_CODES = ["07", "27", "29", "33", "06", "24", "09", "19"]

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

if __name__ == "__main__":
    print(create_vendors(N_VENDORS))