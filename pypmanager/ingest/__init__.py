"""Code for ingesting data."""

from .market_data import async_download_market_data

__all__ = ["async_download_market_data"]
