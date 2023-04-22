"""Example loader."""
import pandas as pd

from pypmanager.security import Security

df = pd.read_csv('data/avanza.csv', sep=";")

NORMALISED_COL_NAMES = {
    "Datum": "transaction_date",
    'Konto': 'account',
    "Typ av transaktion": "transaction_type",
    "Värdepapper/beskrivning": "name",
    "Antal": "no_traded",
    "Kurs": "price",
    "Belopp": "amount",
    "Courtage": "commission",
    "Valuta": "currency",
    "ISIN": "isin_code",
    "Resultat": "pnl",
}
df = df.rename(columns=NORMALISED_COL_NAMES)
df.set_index('transaction_date', inplace=True)

df = df.query("transaction_type == 'Köp' or transaction_type == 'Sälj'")

# Replace dashes with 0
for col in ("commission", "pnl", "isin_code"):
    df[col] = df[col].str.replace('-', '').replace('', 0)

# Make sure numbers have dots, not commas
for col in ('no_traded', 'price', "amount", "commission", "pnl"):
    df[col].replace(',', '.', regex=True, inplace=True)

# Cast datatypes
dtypes_dict = {
    'account': str,
    "transaction_type": str,
    "name": str,
    "no_traded": float,
    "price": float,
    "amount": float,
    "commission": float,
    "currency": str,
    "isin_code": str,
    "pnl": float,
}

# Change the data types of the columns using the dictionary
df = df.astype(dtypes_dict)

for isin in ():
    security_data = Security(
        isin=isin,
        all_data=df,
    )

    print(f"Security: {security_data.name} | {isin}")
    print(f"    Last transaction: {security_data.last_transaction_date}")
    print(f"    Current holding: {security_data.current_holdings}")
    print(f"    No transactions: {security_data.total_transactions}")
    print(f"    Average price: {security_data.average_price}")
    print(f"    Current market value: {security_data.market_value}")
    print(f"    PnL: {security_data.total_pnl}")
    print(f"       ... realized: {security_data.realized_pnl}")
    print(f"       ... unrealized {security_data.unrealized_pnl}")
    print("")
