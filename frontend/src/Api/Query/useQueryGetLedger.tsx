import { LedgerRow, LocalApolloClient } from "@Api";
import { QueryHookOptions, QueryResult, useQuery } from "@apollo/client";
import gql from "graphql-tag";

const QUERY = gql`
  query QueryAllGeneralLedger {
    allGeneralLedger {
      transactionDate
      broker
      source
      action
      name
      noTraded
      aggBuyVolume
      amount
      commission
      cashFlow
      fx
      averageFxRate
      account
      credit
      debit
    }
  }
`;

interface AllAvailableReports {
  allGeneralLedger: LedgerRow[];
}

/**
 * Custom hook to perform a GraphQL query to fetch all general ledger entries.
 * @returns The result of the Apollo useQuery hook, providing loading state, error information,
 * and the data of all general ledger entries as `AllAvailableReports`.
 */
export default function useQueryGetLedger(): QueryResult<AllAvailableReports> {
  const options: QueryHookOptions<AllAvailableReports> = {
    fetchPolicy: "network-only",
    client: LocalApolloClient,
  };

  return useQuery<AllAvailableReports>(QUERY, options);
}
