import type { ChartHistoryRow, Holding, SecurityInfo } from "@Api";
import { LocalApolloClient } from "@Api";
import { useQuery } from "@apollo/client/react";
import gql from "graphql-tag";

const QUERY = gql`
  query GetChartHistory(
    $isinCode: String!
    $startDate: String!
    $endDate: String!
  ) {
    getMyHolding(isinCode: $isinCode) {
      quantityHeld
      costBaseAverage
      investedAmount
      currentMarketValueAmount
    }
    securityInfo(isinCode: $isinCode) {
      isinCode
      name
      currency
    }
    chartHistory(
      isinCode: $isinCode
      startDate: $startDate
      endDate: $endDate
    ) {
      yVal
      xVal
      volumeBuy
      volumeSell
      dividendPerSecurity
      costPriceAverage
    }
  }
`;

interface ChartHistoryData {
  getMyHolding: Holding;
  securityInfo: SecurityInfo;
  chartHistory: ChartHistoryRow[];
}

interface ChartHistoryVariables {
  isinCode: string;
  startDate: string;
  endDate: string;
}

/**
 * Custom hook to fetch chart history data using GraphQL.
 * @param variables - The variables for the GraphQL query.
 * @param variables.isinCode - The ISIN code of the security.
 * @param variables.startDate - The start date for the query in YYYY-MM-DD format.
 * @param variables.endDate - The end date for the query in YYYY-MM-DD format.
 * @returns Chart data rows.
 */
export default function useQueryChartHistory(
  variables: ChartHistoryVariables,
): useQuery.Result<ChartHistoryData> {
  const options = {
    fetchPolicy: "network-only" as const,
    client: LocalApolloClient,
    variables,
  };

  return useQuery<ChartHistoryData>(QUERY, options);
}
