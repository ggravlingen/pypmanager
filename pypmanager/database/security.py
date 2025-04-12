"""Database for daily portfolio holdings."""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

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


class SecurityModel(Base):
    """SQLAlchemy model for securities."""

    __tablename__ = "security"

    isin_code: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    currency: Mapped[str] = mapped_column()

    def __repr__(self) -> str:
        """Return a string representation of the model."""
        return (
            f"<SecurityModel(isin_code={self.isin_code}, name={self.name}, "
            f"currency={self.currency})>"
        )


class AsyncDbSecurity:
    """Database operations for security."""

    def __init__(self) -> None:
        """Initialize the security database."""
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
                SecurityModel.__tablename__,
            )

            if not table_exists:
                await conn.run_sync(Base.metadata.create_all)
                LOGGER.info("Security database created")

        return self

    async def __aexit__(
        self: Self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Exit context manager."""
        await self.engine.dispose()

    async def async_store_data(self, data: list[SecurityModel]) -> None:
        """Store data in the database."""
        async with self.async_session() as session, session.begin():
            await async_upsert_data(session=session, data_list=data)

    async def async_filter_all(self) -> list[SecurityModel]:
        """Return all data in table."""
        async with self.async_session() as session, session.begin():
            query = f"SELECT * FROM {SecurityModel.__tablename__}"  # noqa: S608

            # Execute query
            result = await session.execute(text(query))
            rows = result.fetchall()

            # Map rows to MarketDataModel objects
            return [
                SecurityModel(
                    isin_code=row.isin_code,
                    name=row.name,
                    currency=row.currency,
                )
                for row in rows
            ]

    async def _async_purge_table(self) -> None:
        """
        Cleanup the database.

        Only to be used in tests!
        """
        async with self.async_session() as session, session.begin():
            stmt = delete(SecurityModel)
            await session.execute(stmt)
            await session.commit()
