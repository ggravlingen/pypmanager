"""Main."""

import argparse
import asyncio

from pypmanager.helpers.market_data import (
    async_download_market_data,
    async_sync_csv_to_db,
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyse portfolio data.")

    parser.add_argument(
        "--load",
        "-l",
        action="store_true",
        help="Load market data",
    )

    parser.add_argument(
        "--sync",
        "-s",
        action="store_true",
        help="Sync market data from csv into database",
    )

    all_args = parser.parse_args()

    if all_args.load:
        asyncio.run(async_download_market_data())

    if all_args.sync:
        asyncio.run(async_sync_csv_to_db())
