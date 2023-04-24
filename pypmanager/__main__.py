"""Main."""

from pypmanager.data_loader import load_data
from pypmanager.holding import Holding
from pypmanager.reports.cmd_line import print_pretty_table

all_data, all_securities = load_data()

calc_security_list: list[Holding] = []
for security_name in all_securities:
    calc_security_list.append(
        Holding(
            name=security_name,
            all_data=all_data,
        )
    )

print_pretty_table(calc_security_list)
