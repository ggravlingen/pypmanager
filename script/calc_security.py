"""Example loader."""
import pandas as pd

from pypmanager.data_loader import AvanzaLoader, LysaLoader, MiscLoader
from pypmanager.portfolio import Portfolio
from pypmanager.security import Security

df_a = AvanzaLoader().df
df_b = LysaLoader().df
df_c = MiscLoader().df

all_data = pd.concat([df_a, df_b, df_c])

all_securities = all_data.name.unique()
# all_securities = ["BGF World Gold A2"]


calc_security_list: list[Security] = []
for security_name in all_securities:
    calc_security_list.append(
        Security(
            name=security_name,
            all_data=all_data,
        )
    )


sorted_security_list = sorted(calc_security_list, key=lambda x: x.name)


for security_data in sorted_security_list:
    print(f"{security_data.name} | {security_data.isin_code}")
    print(f"    First transaction: {security_data.date_first_transaction}")
    print(f"    Last transaction: {security_data.date_last_transaction}")
    print(f"    Invested amount: {security_data.invested_amount}")
    print(f"    Current holding: {security_data.current_holdings}")
    print(f"    No transactions: {security_data.total_transactions}")
    print(f"    Average price: {security_data.average_price}")
    print(f"    Current market value: {security_data.market_value}")
    print(f"    PnL: {security_data.total_pnl}")
    print(f"       ... realized: {security_data.realized_pnl}")
    print(f"       ... unrealized {security_data.unrealized_pnl}")
    print("")

portfolio = Portfolio(securities=calc_security_list)

print(f"Realized PnL: {portfolio.realized_pnl / 1e6}")
print(f"Unrealized PnL: {portfolio.unrealized_pnl / 1e6}")
print(f"Invested amount: {round(portfolio.invested_amount / 1e6, 2)}")

all_isin = all_data.isin_code.unique()
