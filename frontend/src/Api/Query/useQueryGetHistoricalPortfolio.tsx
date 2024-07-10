import { HistoricalPortfolioRow, LocalApolloClient } from "@Api";
import { QueryHookOptions, QueryResult, useQuery } from "@apollo/client";
import gql from "graphql-tag";

const QUERY = gql`
  query QueryHistoricalPortfolio {
    historicalPortfolio {
      reportDate
      invested_amount
      marketValue
      returnPct
      totalPnl
      realizedPnl
      unrealizedPnl
    }
  }
`;

interface QueryHistoricalPortfolio {
  historicalPortfolio: HistoricalPortfolioRow[];
}

/**
 * Custom hook for performing a GraphQL query to fetch historical portfolio data.
 *
 * This hook utilizes Apollo's `useQuery` to fetch data with a "network-only" fetch policy,
 * ensuring the data is always retrieved from the network rather than the cache.
 * @returns The result of the query, including loading,
 * error states, and the fetched data.
 */
export default function useQueryGetHistoricalPortfolio(): QueryResult<QueryHistoricalPortfolio> {
  const options: QueryHookOptions<QueryHistoricalPortfolio> = {
    fetchPolicy: "network-only",
    client: LocalApolloClient,
  };

  return useQuery<QueryHistoricalPortfolio>(QUERY, options);
}
