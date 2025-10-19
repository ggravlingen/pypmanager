import type { Holding } from "@Api";
import { LocalApolloClient } from "@Api";
import { useQuery } from "@apollo/client/react";
import gql from "graphql-tag";

const QUERY = gql`
  query QueryCurrentPortfolio {
    currentPortfolio {
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

interface PortfolioHoldings {
  currentPortfolio: Holding[];
}

/**
 * Custom hook to fetch portfolio holdings data.
 *
 * This hook utilizes Apollo's useQuery to fetch portfolio holdings from a GraphQL endpoint.
 * It is configured to always fetch from the network (ignoring the cache) to ensure the data
 * is up-to-date. It uses a predefined GraphQL query and a local Apollo client instance for the request.
 * @returns The query result object containing loading state, error information, and the fetched data.
 */
export default function useQueryGetPortfolio(): useQuery.Result<PortfolioHoldings> {
  const options = {
    fetchPolicy: "network-only" as const,
    client: LocalApolloClient,
  };

  return useQuery<PortfolioHoldings>(QUERY, options);
}
