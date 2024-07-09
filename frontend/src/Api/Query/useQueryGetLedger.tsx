import { useQuery, QueryHookOptions, QueryResult } from "@apollo/client";
import gql from "graphql-tag";
import { LedgerRow } from "../Models/ledger";
import ApolloClient from "../ApolloClient/Client";

const QUERY = gql`
  query QueryAllGeneralLedger {
    allGeneralLedger {
      date
      broker
      source
    }
  }
`;

interface AllAvailableReports {
  allGeneralLedger: LedgerRow[];
}

/**
 * Custom hook to perform a GraphQL query to fetch all general ledger entries.
 *
 * @returns The result of the Apollo useQuery hook, providing loading state, error information,
 * and the data of all general ledger entries as `AllAvailableReports`.
 */
export default function useQueryGetLedger(): QueryResult<AllAvailableReports> {
  const options: QueryHookOptions<AllAvailableReports> = {
    fetchPolicy: "network-only",
    client: ApolloClient,
  };

  return useQuery<AllAvailableReports>(QUERY, options);
}
