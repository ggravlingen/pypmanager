import { ChartHistoryRow, LocalApolloClient } from "@Api";
import { QueryHookOptions, QueryResult, useQuery } from "@apollo/client";
import gql from "graphql-tag";

const QUERY = gql`
  query GetChartHistory(
    $isinCode: String!
    $startDate: String!
    $endDate: String!
  ) {
    chartHistory(
      isinCode: $isinCode
      startDate: $startDate
      endDate: $endDate
    ) {
      yVal
      xVal
      volumeBuy
      volumeSell
    }
  }
`;

interface ChartHistoryData {
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
): QueryResult<ChartHistoryData> {
  const options: QueryHookOptions<ChartHistoryData> = {
    fetchPolicy: "network-only",
    client: LocalApolloClient,
    variables,
  };

  return useQuery<ChartHistoryData>(QUERY, options);
}
