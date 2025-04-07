"""Database for market data."""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import TYPE_CHECKING, Self

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


class MarketDataModel(Base):
    """SQLAlchemy model for market data."""

    __tablename__ = "market_data"

    isin: Mapped[str] = mapped_column(primary_key=True)
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

    async def store_market_data(self, data: list[MarketDataModel]) -> None:
        """Store market data in the database."""
        models = [
            MarketDataModel(
                isin=item.isin,
                close_price=item.close_price,
                report_date=item.report_date,
                date_added=datetime.now(tz=UTC).date(),
                source=item.source,
            )
            for item in data
        ]

        async with self.async_session() as session, session.begin():
            await async_upsert_data(session=session, data_list=models)

    async def get_market_data(
        self, isin: str, report_date: date
    ) -> MarketDataModel | None:
        """Get market data from the database."""
        async with self.async_session() as session, session.begin():
            if data := await session.get(MarketDataModel, (isin, report_date)):
                return MarketDataModel(
                    isin=data.isin,
                    close_price=data.close_price,
                    report_date=data.report_date,
                    date_added=data.date_added,
                    source=data.source,
                )

            return None
