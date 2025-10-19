import type { TransactionRow } from "@Api";
import { LocalApolloClient } from "@Api";
import { useQuery } from "@apollo/client/react";
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
export default function useQueryGetAllTransaction(): useQuery.Result<AllTransactions> {
  const options = {
    fetchPolicy: "network-only" as const,
    client: LocalApolloClient,
  };

  return useQuery<AllTransactions>(QUERY, options);
}
