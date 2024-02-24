"""A GraphQL API."""

import strawberry
from strawberry.asgi import GraphQL

from .query import Query

schema = strawberry.Schema(query=Query)
graphql_app = GraphQL(schema)  # type: ignore[var-annotated]


__all__ = ["graphql_app"]
