import { LocalApolloClient, TransactionRow } from "@Api";
import { QueryHookOptions, QueryResult, useQuery } from "@apollo/client";
import gql from "graphql-tag";

const QUERY = gql`
  query QueryAllTransaction {
    allTransaction {
      transactionDate
      isinCode
      broker
      source
      action
      name
      noTraded
      currency
      price
      commission
      fx
      cashFlow
      costBaseAverage
      quantityHeld
      pnlTotal
      pnlTrade
      pnlDividend
    }
  }
`;

interface AllTransactions {
  allTransaction: TransactionRow[];
}

/**
 * Custom hook to fetch all transactions.
 *
 * This hook encapsulates the logic for querying all transactions, returning a `QueryResult` object
 * that includes the transaction data along with metadata such as loading status and errors.
 * @returns An object containing the transactions data, loading status, and any errors encountered during the query.
 */
export default function useQueryGetAllTransaction(): QueryResult<AllTransactions> {
  const options: QueryHookOptions<AllTransactions> = {
    fetchPolicy: "network-only",
    client: LocalApolloClient,
  };

  return useQuery<AllTransactions>(QUERY, options);
}
