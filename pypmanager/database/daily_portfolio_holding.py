"""Database for daily portfolio holdings."""

from __future__ import annotations

from datetime import date  # noqa: TC003
from typing import TYPE_CHECKING, Any, Self

from sqlalchemy import delete, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Mapped, mapped_column

from pypmanager.settings import Settings

from .utils import LOGGER, Base, async_upsert_data, check_table_exists

if TYPE_CHECKING:
    from types import TracebackType


class DailyPortfolioMoldingModel(Base):
    """SQLAlchemy model for daily portfolio holdings."""

    __tablename__ = "daily_portfolio_holdings"

    isin_code: Mapped[str] = mapped_column(primary_key=True)
    report_date: Mapped[date] = mapped_column(primary_key=True)
    no_held: Mapped[float]

    def __repr__(self) -> str:
        """Return a string representation of the model."""
        return (
            f"<MarketDataModel(isin_code={self.isin_code}, "
            f"report_date={self.report_date}, no_held={self.no_held})>"
        )


class AsyncDbDailyPortfolioHolding:
    """Database operations for daily portfolio holdings."""

    def __init__(self) -> None:
        """Initialize the daily portfolio holdings database."""
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
                DailyPortfolioMoldingModel.__tablename__,
            )

            if not table_exists:
                await conn.run_sync(Base.metadata.create_all)
                LOGGER.info("Daily portfolio holdings database schema created")

        return self

    async def __aexit__(
        self: Self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Exit context manager."""
        await self.engine.dispose()

    async def async_store_data(self, data: list[DailyPortfolioMoldingModel]) -> None:
        """Store data in the database."""
        models = [
            DailyPortfolioMoldingModel(
                isin_code=item.isin_code,
                report_date=item.report_date,
                no_held=item.no_held,
            )
            for item in data
        ]

        async with self.async_session() as session, session.begin():
            await async_upsert_data(session=session, data_list=models)

    async def async_filter_all(
        self,
        isin_code: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[DailyPortfolioMoldingModel]:
        """Return all data in table."""
        async with self.async_session() as session, session.begin():
            query = (
                f"SELECT * FROM {DailyPortfolioMoldingModel.__tablename__} "  # noqa: S608
                "WHERE 1=1"
            )
            params: dict[str, Any] = {}

            # Add filters dynamically
            if isin_code:
                query += " AND isin_code = :isin_code"
                params["isin_code"] = isin_code
            if start_date:
                query += " AND report_date >= :start_date"
                params["start_date"] = start_date
            if end_date:
                query += " AND report_date <= :end_date"
                params["end_date"] = end_date

            # Add ordering
            query += " ORDER BY report_date DESC"

            # Execute query
            result = await session.execute(text(query), params)
            rows = result.fetchall()

            # Map rows to MarketDataModel objects
            return [
                DailyPortfolioMoldingModel(
                    isin_code=row.isin_code,
                    report_date=row.report_date,
                    no_held=row.no_held,
                )
                for row in rows
            ]

    async def _async_purge_table(self) -> None:
        """
        Cleanup the database.

        Only to be used in tests!
        """
        async with self.async_session() as session, session.begin():
            stmt = delete(DailyPortfolioMoldingModel)
            await session.execute(stmt)
            await session.commit()
