"""Main."""

import argparse
import asyncio

from pypmanager.ingest.market_data import async_download_market_data

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
        asyncio.run(async_download_market_data())
