import type { ResultStatementRow } from "@Api";
import { LocalApolloClient } from "@Api";
import type { QueryHookOptions, QueryResult } from "@apollo/client";
import { useQuery } from "@apollo/client";
import gql from "graphql-tag";

const QUERY = gql`
  query QueryResultStatement {
    resultStatement {
      itemName
      yearList
      amountList
      isTotal
    }
  }
`;

interface ResultStatementData {
  resultStatement: ResultStatementRow[];
}

/**
 * Custom hook for querying the income statement data.
 * @returns The query result containing the income statement data.
 */
export default function useQueryGetIncomeStatement(): QueryResult<ResultStatementData> {
  const options: QueryHookOptions<ResultStatementData> = {
    fetchPolicy: "network-only",
    client: LocalApolloClient,
  };

  return useQuery<ResultStatementData>(QUERY, options);
}
