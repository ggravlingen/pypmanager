"""Main."""
import argparse
from datetime import datetime

from pypmanager.holding import Holding
from pypmanager.loader_market_data import market_data_loader
from pypmanager.loader_transaction import load_data
from pypmanager.reports import print_pretty_table

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyse portfolio data.")

    parser.add_argument(
        "--load",
        "-l",
        action="store_true",
        help="Load market data",
    )
    parser.add_argument(
        "--analyze",
        "-a",
        action="store_true",
        help="Analyze portfolio",
    )
    parser.add_argument(
        "--report_date",
        "-r",
        type=str,
        help="Report date for analysis in yyyy-mm-dd format",
    )

    all_args = parser.parse_args()

    if all_args.load:
        market_data_loader()

    if all_args.analyze:
        report_date = (
            datetime.strptime(all_args.report_date, "%Y-%m-%d")
            if all_args.report_date
            else None
        )

        all_data, all_securities = load_data(report_date=report_date)

        calc_security_list: list[Holding] = []
        for security_name in all_securities:
            calc_security_list.append(
                Holding(
                    name=security_name,
                    all_data=all_data,
                    report_date=report_date,
                )
            )

        print_pretty_table(calc_security_list)
