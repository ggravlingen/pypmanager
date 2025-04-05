import type { Holding } from "@Api";
import { LocalApolloClient } from "@Api";
import type { QueryHookOptions, QueryResult } from "@apollo/client";
import { useQuery } from "@apollo/client";
import gql from "graphql-tag";

const QUERY = gql`
  query QueryGetMyHolding {
    getMyHolding {
      name
      isinCode
      quantityHeld
      costBaseAverage
      investedAmount
      currentMarketValueAmount
      pnlTotal
      pnlTrade
      pnlDividend
      pnlUnrealized
      marketValueDate
      marketValuePrice
    }
  }
`;

interface MyHolding {
  currentPortfolio: Holding;
}

/**
 * Custom hook to fetch holdings data for one security.
 *
 * This hook utilizes Apollo's useQuery to fetch portfolio holdings from a GraphQL endpoint.
 * It is configured to always fetch from the network (ignoring the cache) to ensure the data
 * is up-to-date. It uses a predefined GraphQL query and a local Apollo client instance for the request.
 * @returns The query result object containing loading state, error information, and the fetched data.
 */
export default function useQueryGetMyHolding(): QueryResult<MyHolding> {
  const options: QueryHookOptions<MyHolding> = {
    fetchPolicy: "network-only",
    client: LocalApolloClient,
  };

  return useQuery<MyHolding>(QUERY, options);
}
