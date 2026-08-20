"""
Derives two divergent copies of the ground-truth invoice dataset-
  1. purchase_register.csv - company's own books
  2. gstr_2a.csv - the government's record, built from supplier filings

Mismatches are introduced INDEPENDENTLY per file: each ground-truth invoice is
assigned exactly one outcome category, and that category determines how the
invoice looks (or whether it appears at all) in each of the two derived files.
Distribution is hardcoded per the project spec (not randomized within a range):

    85% exact match           (850 invoices) — identical in both files
     6% missing from GSTR-2A  ( 60 invoices) — present in PR only
     3% missing from PR       ( 30 invoices) — present in 2A only
     3% amount mismatch       ( 30 invoices) — tax altered in ONE copy
     2% date/period mismatch  ( 20 invoices) — filing_period shifted in ONE copy
     1% duplicate             ( 10 invoices) — row copied twice within ONE file

`ground_truth_id` is carried into both output files as an answer key for
validating the SQL matching engine later. It is NOT a real-world field —
the matching engine (v1) must key strictly on (vendor_gstin + invoice_number),
same as it would have to in production, where PR and GSTR-2A share no
common row ID.
"""

import random
import pandas as pd
import numpy as np

random.seed(69)
np.random.seed(69)

GROUND_TRUTH_PATH = "./data/ground_truth.csv"

CATEGORY_COUNTS = {
    "exact" : 850,
    "missing_from_2a" : 60,
    "missing_from_pr" : 30,
    "amount_mismatch" : 30,
    "date_mismatch" : 20,
    "duplicate" : 10
}

def assign_mismatch_categories(ground_truth: pd.DataFrame, mismatch_counts: dict) -> dict:
    """
    Given the ground truth invoices and a dict of {category : count},
    randomly assigns each invoice to at most one mismatch category.
    Returns {category : [list of invoice_ids]}
    """
    assigned_ids = {}
    already_picked = set()
    # amount_mismatch = ground_truth.sample(n=30, axis=0, replace=False)

    for category, count in mismatch_counts.items():
        available = ground_truth.loc[~ground_truth["invoice_id"].isin(already_picked)]
        sampled = available.sample(n=count)
        sampled_ids = sampled["invoice_id"].tolist()
        assigned_ids[category] = sampled_ids
        already_picked.update(sampled_ids)

    return assigned_ids

def build_gstr_2a(ground_truth: pd.DataFrame, assigned_ids: dict) -> pd.DataFrame:
    gstr_2a = ground_truth.copy()
    gstr_2a = gstr_2a.loc[~gstr_2a["invoice_id"].isin(assigned_ids["missing_from_2a"])]
    return gstr_2a

def build_purchase_register(ground_truth: pd.DataFrame, assigned_ids: dict) -> pd.DataFrame():
    purchase_reg = ground_truth.copy()
    mask = purchase_reg["invoice_id"].isin(assigned_ids["amount_mismatch"])
    n_rows = mask.sum()
    factors = np.random.uniform(0.10, 0.40, size=n_rows) * np.random.choice([-1, 1], size=n_rows)
    purchase_reg.loc[mask, "taxable_value"] = purchase_reg.loc[mask, "taxable_value"] * (1 + factors)
    return purchase_reg

if __name__ == "__main__":
    ground_truth = pd.read_csv(GROUND_TRUTH_PATH)
    assigned_ids = assign_mismatch_categories(ground_truth=ground_truth, mismatch_counts=CATEGORY_COUNTS)
    for k, v in assigned_ids.items():
        print(k, len(v), type(v))
    gstr_2a = build_gstr_2a(ground_truth=ground_truth, assigned_ids=assigned_ids)
    purchase_register = build_purchase_register(ground_truth=ground_truth, assigned_ids=assigned_ids)
    print(purchase_register.head())



