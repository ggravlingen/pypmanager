import type { ResultStatementRow } from "@Api";
import { LocalApolloClient } from "@Api";
import { useQuery } from "@apollo/client/react";
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
export default function useQueryGetIncomeStatement(): useQuery.Result<ResultStatementData> {
  const options = {
    fetchPolicy: "network-only" as const,
    client: LocalApolloClient,
  };

  return useQuery<ResultStatementData>(QUERY, options);
}
