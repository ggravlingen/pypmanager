"""Database for market data."""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import TYPE_CHECKING, Any, Self

from sqlalchemy import Row, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Mapped, mapped_column

from pypmanager.settings import Settings

from .utils import LOGGER, Base, async_upsert_data, check_table_exists

if TYPE_CHECKING:
    from collections.abc import Sequence
    from types import TracebackType


class MarketDataModel(Base):
    """SQLAlchemy model for market data."""

    __tablename__ = "market_data"

    isin_code: Mapped[str] = mapped_column(primary_key=True)
    report_date: Mapped[date] = mapped_column(primary_key=True)
    close_price: Mapped[float]
    currency: Mapped[float | None] = mapped_column(default=None)
    date_added: Mapped[date] = mapped_column()
    source: Mapped[str] = mapped_column()


class AsyncMarketDataDB:
    """Database operations for market data."""

    def __init__(self) -> None:
        """Initialize the market data database."""
        self.engine = create_async_engine(
            f"sqlite+aiosqlite:///{Settings.database_local}"
        )
        self.async_session = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def __aenter__(self) -> Self:
        """Enter context manager."""
        async with self.engine.begin() as conn:
            table_exists = await conn.run_sync(
                check_table_exists,
                MarketDataModel.__tablename__,
            )

            if not table_exists:
                await conn.run_sync(Base.metadata.create_all)
                LOGGER.info("Market data database schema created")

        return self

    async def __aexit__(
        self: Self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Exit context manager."""
        await self.engine.dispose()

    async def async_store_market_data(self, data: list[MarketDataModel]) -> None:
        """Store market data in the database."""
        models = [
            MarketDataModel(
                isin_code=item.isin_code,
                close_price=item.close_price,
                report_date=item.report_date,
                date_added=datetime.now(tz=UTC).date(),
                source=item.source,
            )
            for item in data
        ]

        async with self.async_session() as session, session.begin():
            await async_upsert_data(session=session, data_list=models)

    async def async_get_market_data(
        self, isin_code: str, report_date: date
    ) -> MarketDataModel | None:
        """Return market data for a specific day."""
        async with self.async_session() as session, session.begin():
            if data := await session.get(MarketDataModel, (isin_code, report_date)):
                return MarketDataModel(
                    isin_code=data.isin_code,
                    close_price=data.close_price,
                    report_date=data.report_date,
                    date_added=data.date_added,
                    source=data.source,
                )

            return None

    async def async_get_last_close_price_by_isin(self) -> Sequence[Row[Any]]:
        """
        Return the last close price data on ISIN code level.

        Example:
        report date | isin_code | price
        2023-01-01 | US0378331005 | 150.25
        2023-01-01 | US0378331003 | 150.00
        """
        async with self.async_session() as session, session.begin():
            result = await session.execute(
                text("""
                        SELECT
                            md.isin_code,
                            md.report_date,
                            md.close_price
                        FROM
                            market_data md
                        JOIN (
                            SELECT
                                isin_code,
                                MAX(report_date) AS latest_date
                            FROM
                                market_data
                            GROUP BY
                                isin_code
                        ) latest_dates
                            ON md.isin_code = latest_dates.isin_code
                            AND md.report_date = latest_dates.latest_date;
                        """)
            )

            return result.fetchall()
