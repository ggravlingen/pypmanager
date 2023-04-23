"""Example loader."""
import pandas as pd

from pypmanager.data_loader import AvanzaLoader, LysaLoader, MiscLoader
from pypmanager.holding import Holding
from pypmanager.reports.cmd_line import print_pretty_table

df_a = AvanzaLoader().df
df_b = LysaLoader().df
df_c = MiscLoader().df

all_data = pd.concat([df_a, df_b, df_c])

all_securities = all_data.name.unique()


calc_security_list: list[Holding] = []
for security_name in all_securities:
    calc_security_list.append(
        Holding(
            name=security_name,
            all_data=all_data,
        )
    )

print_pretty_table(calc_security_list)
