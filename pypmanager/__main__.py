"""Main."""
import argparse

from pypmanager.data_loader import load_data
from pypmanager.holding import Holding
from pypmanager.loaders import market_data_loader
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

    all_args = parser.parse_args()

    if all_args.load:
        market_data_loader()

    if all_args.analyze:
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
