"""Helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import pandas as pd
import yaml

from pypmanager.analytics.holding import Holding
from pypmanager.analytics.portfolio import Portfolio
from pypmanager.error import DataError
from pypmanager.loader_market_data.models import Sources
from pypmanager.loader_transaction import (
    AvanzaLoader,
    GeneralLedger,
    GenericLoader,
    LysaLoader,
)
from pypmanager.loader_transaction.const import ColumnNameValues
from pypmanager.settings import Settings
from pypmanager.utils.dt import async_get_last_n_quarters

if TYPE_CHECKING:
    from pypmanager.loader_market_data.base_loader import BaseMarketDataLoader
    from pypmanager.loader_market_data.models import Source, SourceData

LOGGER = logging.getLogger(__package__)


def _load_sources() -> list[Source]:
    """Load settings."""
    path = Path(Settings.file_market_data_config)
    with path.open(encoding="UTF-8") as file:
        # Load the YAML content from the file
        yaml_data = yaml.safe_load(file)

        data = Sources(**yaml_data)

        return data.sources


def _class_importer(name: str) -> Any:  # noqa: ANN401
    """
    Load a class from a string representing a fully qualified class name.

    :param class_path: The fully qualified name of the class to load and instantiate.
    :return: An instance of the specified class.
    """
    # Split the class path into its individual components.
    components = name.split(".")
    class_name = components.pop()
    module_name = ".".join(components)

    # Dynamically load the module.
    module = __import__(module_name, fromlist=[class_name])

    # Get the class from the module.
    return getattr(module, class_name)


class UpdateMarketDataCsv:
    """Helper class to update a CSV file containing market data."""

    df_all_data: pd.DataFrame
    df_existing_file: pd.DataFrame
    df_source_data: pd.DataFrame

    def __init__(
        self: UpdateMarketDataCsv, data: list[SourceData], source_name: str
    ) -> None:
        """Init class."""
        self.data = data
        self.source_name = source_name

        self.file_market_data = Settings.dir_market_data / f"{source_name}.csv"

        self.prepare_source_data()
        self.concat_data()
        self.save_to_csv()

    @property
    def target_file_exists(self: UpdateMarketDataCsv) -> bool:
        """Check if the target file exists."""
        return self.file_market_data.exists()

    def prepare_source_data(self: UpdateMarketDataCsv) -> None:
        """Convert source data to a data frame."""
        self.df_source_data = pd.DataFrame([vars(s) for s in self.data])

        # Add a timestamp for when we added the date
        self.df_source_data["date_added_utc"] = datetime.now(UTC)
        self.df_source_data["source"] = self.source_name

    def concat_data(self: UpdateMarketDataCsv) -> None:
        """Merge existing data, if existing, with new data."""
        if self.target_file_exists:
            existing_df = pd.read_csv(
                self.file_market_data,
                sep=";",
                parse_dates=["report_date"],
            )
        else:
            existing_df = pd.DataFrame(
                data=[],
                columns=["isin_code", "price", "report_date", "name", "date_added_utc"],
            )

        self.df_all_data = pd.concat([existing_df, self.df_source_data])

    def save_to_csv(self: UpdateMarketDataCsv) -> None:
        """Save data to CSV."""
        df_final_output = self.df_all_data.copy()

        # Remove duplicates
        df_final_output = df_final_output.drop_duplicates(
            subset=["isin_code", "report_date"], keep="last"
        )

        df_final_output = df_final_output.sort_values(["isin_code", "report_date"])

        # Write the merged DataFrame back to the CSV file
        df_final_output.to_csv(self.file_market_data, index=False, sep=";")


def load_transaction_files(report_date: datetime | None = None) -> pd.DataFrame:
    """Load all transaction files into a Dataframe."""
    return cast(
        pd.DataFrame,
        pd.concat(
            [
                GenericLoader(report_date).df_final,
                AvanzaLoader(report_date).df_final,
                LysaLoader(report_date).df_final,
            ],
        ),
    )


def get_general_ledger(report_date: datetime | None = None) -> pd.DataFrame:
    """Return the general ledger."""
    all_data = load_transaction_files(report_date=report_date)
    return GeneralLedger(transactions=all_data).output_df


def get_general_ledger_as_dict() -> list[dict[str, Any]]:
    """Get the general ledger converted to dict."""
    df_general_ledger = get_general_ledger()
    df_general_ledger = df_general_ledger.sort_values(
        [
            ColumnNameValues.TRANSACTION_DATE,
            ColumnNameValues.NAME,
        ],
        ascending=False,
    )
    output_dict = df_general_ledger.reset_index().to_dict(orient="records")

    return cast(list[dict[str, Any]], output_dict)


async def get_holdings(report_date: date | None = None) -> list[Holding]:
    """Return a list of current holdings."""
    df_general_ledger = get_general_ledger()
    all_securities = cast(list[str], df_general_ledger[ColumnNameValues.NAME].unique())

    holdings: list[Holding] = []
    for security_name in all_securities:
        holding = Holding(
            name=security_name,
            df_general_ledger=df_general_ledger,
            report_date=report_date,
        )

        if holding.total_pnl == 0:
            continue

        holdings.append(holding)

    # Order by name
    return sorted(holdings, key=lambda x: x.name)


async def download_market_data() -> None:
    """Load JSON-data from a source."""
    sources = _load_sources()

    for idx, source in enumerate(sources):
        LOGGER.info(
            f"{idx}: Parsing {source.isin_code} using "
            f"{source.loader_class.replace('pypmanager.loader_market_data.', '')}",
        )

        try:
            data_loader_klass = _class_importer(source.loader_class)
        except AttributeError as err:
            msg = "Unable to load data"
            raise DataError(msg, err) from err

        try:
            loader: BaseMarketDataLoader = data_loader_klass(
                lookup_key=source.lookup_key,
                isin_code=source.isin_code,
                name=source.name,
            )
            UpdateMarketDataCsv(data=loader.to_source_data(), source_name=loader.source)
        except AttributeError:
            LOGGER.exception(f"Unable to load {loader}")


@dataclass
class PortfolioSnapshot:
    """A point of time snapshot of a portfolio."""

    report_date: date
    portfolio: Portfolio


async def get_historical_portfolio() -> list[PortfolioSnapshot]:
    """Return a list of historical portfolios."""
    quarter_list = await async_get_last_n_quarters(no_quarters=8)
    quarter_list.append(datetime.now(UTC).date())

    portfolio_data: list[PortfolioSnapshot] = []
    for report_date in quarter_list:
        holdings = await get_holdings(report_date=report_date)
        portfolio = Portfolio(holdings=holdings)
        portfolio_data.append(
            PortfolioSnapshot(
                report_date=report_date,
                portfolio=portfolio,
            ),
        )

    return portfolio_data
