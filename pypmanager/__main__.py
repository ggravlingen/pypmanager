"""Main."""
import argparse

from pypmanager.loader_market_data import market_data_loader

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyse portfolio data.")

    parser.add_argument(
        "--load",
        "-l",
        action="store_true",
        help="Load market data",
    )

    all_args = parser.parse_args()

    if all_args.load:
        market_data_loader()
