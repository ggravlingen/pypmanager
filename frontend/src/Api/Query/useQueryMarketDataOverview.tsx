import type { MarketDataOverviewRecord } from "@Api";
import { LocalApolloClient } from "@Api";
import type { QueryHookOptions, QueryResult } from "@apollo/client";
import { useQuery } from "@apollo/client";
import gql from "graphql-tag";

const QUERY = gql`
  query QueryMarketDataOverview {
    marketDataOverview {
      name
      isinCode
      firstDate
      lastDate
      currency
    }
  }
`;

interface Output {
  marketDataOverview: MarketDataOverviewRecord[];
}

/**
 * Custom hook to query market data overview.
 * This hook uses Apollo Client's `useQuery` to fetch market data overview
 * with a network-only fetch policy, ensuring that the data is always fetched
 * from the server and not from the cache.
 * @returns The result of the query, including loading state, error, and data.
 */
export default function useQueryMarketDataOverview(): QueryResult<Output> {
  const options: QueryHookOptions<Output> = {
    fetchPolicy: "network-only",
    client: LocalApolloClient,
  };

  return useQuery<Output>(QUERY, options);
}
