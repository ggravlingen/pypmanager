"""Database for market data."""

from datetime import UTC, date, datetime
import logging
from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from pypmanager.settings import Settings

_LOGGER = logging.getLogger(__name__)


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for SQLAlchemy models."""


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
            await conn.run_sync(Base.metadata.create_all)
            _LOGGER.info("Market data database schema created")

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
            try:
                # SQLAlchemy 2.0 style: merge models to handle "upsert" behavior
                for model in models:
                    await session.merge(model)

                _LOGGER.info(f"Stored {len(data)} market data records")
            except Exception:
                _LOGGER.exception("Failed to store market data")
                raise
