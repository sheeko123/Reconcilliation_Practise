"""
Synthetic Financial Reconciliation Script (Professional Version)
Author: Dara Sheehan 
Purpose: Generate Payments and Ledger data, perform reconciliation with full outer join,
         flag discrepancies (missing payments, missing ledger, amount mismatch), 
         and output clean tables for Power BI dashboard.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# -------------------------------
# 1. Parameters & Setup
# -------------------------------
NUM_MERCHANTS = 5
NUM_TRANSACTIONS = 200
MERCHANTS = [f"M{str(i).zfill(3)}" for i in range(1, NUM_MERCHANTS + 1)]
START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 8, 15)
DISCREPANCY_RATE = 0.1  # 10% of transactions will have discrepancies

# -------------------------------
# 2. Generate Payments Data
# -------------------------------
def generate_payments():
    payments = []
    for _ in range(NUM_TRANSACTIONS):
        merchant = random.choice(MERCHANTS)
        date = START_DATE + timedelta(days=random.randint(0, (END_DATE - START_DATE).days))
        amount = round(random.uniform(50, 500), 2)
        payment_id = f"P{random.randint(1000,9999)}"
        payments.append([payment_id, merchant, date, amount])
    payments_df = pd.DataFrame(payments, columns=['PaymentID', 'Merchant', 'PaymentDate', 'PaymentAmount'])
    return payments_df

payments_df = generate_payments()

# -------------------------------
# 3. Generate Ledger Data
# -------------------------------
def generate_ledger(payments_df):
    ledger = payments_df.copy()
    ledger['LedgerAmount'] = ledger['PaymentAmount']

    # Introduce discrepancies in some transactions
    num_discrepancies = int(NUM_TRANSACTIONS * DISCREPANCY_RATE)
    discrepancy_indices = np.random.choice(ledger.index, num_discrepancies, replace=False)

    for idx in discrepancy_indices:
        ledger.loc[idx, 'LedgerAmount'] = round(ledger.loc[idx, 'LedgerAmount'] * random.uniform(0.8, 1.2), 2)

    # Introduce some missing ledger entries
    missing_indices = np.random.choice(ledger.index, int(num_discrepancies / 2), replace=False)
    ledger.loc[missing_indices, 'LedgerAmount'] = np.nan

    ledger['LedgerDate'] = ledger['PaymentDate']
    ledger_df = ledger[['PaymentID', 'Merchant', 'LedgerDate', 'LedgerAmount']]
    return ledger_df

ledger_df = generate_ledger(payments_df)

# -------------------------------
# 4. Reconciliation (Full Outer Join)
# -------------------------------
recon_df = payments_df.merge(ledger_df, on=['PaymentID', 'Merchant'], how='outer')

# Flag missing payments
recon_df['MissingPayment'] = recon_df['PaymentAmount'].isna()
# Flag missing ledger entries
recon_df['MissingLedger'] = recon_df['LedgerAmount'].isna()
# Flag amount mismatches
recon_df['AmountMismatch'] = (~recon_df['MissingPayment'] & ~recon_df['MissingLedger'] &
                              (recon_df['PaymentAmount'] != recon_df['LedgerAmount']))
# Overall discrepancy
recon_df['Discrepancy'] = recon_df[['MissingPayment', 'MissingLedger', 'AmountMismatch']].any(axis=1)

# -------------------------------
# 5. Summary for Dashboard
# -------------------------------
summary_df = recon_df.groupby('Merchant').agg(
    TotalPayments=('PaymentAmount', 'sum'),
    TotalLedger=('LedgerAmount', 'sum'),
    NumTransactions=('PaymentID', 'count'),
    NumDiscrepancies=('Discrepancy', 'sum'),
    MissingPayments=('MissingPayment', 'sum'),
    MissingLedgerEntries=('MissingLedger', 'sum'),
    AmountMismatches=('AmountMismatch', 'sum')
).reset_index()

summary_df['DiscrepancyPct'] = (summary_df['NumDiscrepancies'] / summary_df['NumTransactions']) * 100

# -------------------------------
# 6. Output CSVs for Power BI
# -------------------------------
payments_df.to_csv('Payments.csv', index=False)
ledger_df.to_csv('Ledger.csv', index=False)
recon_df.to_csv('Reconciliation.csv', index=False)
summary_df.to_csv('ReconciliationSummary.csv', index=False)

print("✅ Synthetic data generated and reconciliation complete (Full Outer Join).")
print("CSV files created: Payments.csv, Ledger.csv, Reconciliation.csv, ReconciliationSummary.csv")
