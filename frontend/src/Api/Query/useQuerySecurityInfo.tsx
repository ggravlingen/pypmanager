import type { SecurityInfo } from "@Api";
import { LocalApolloClient } from "@Api";
import { useQuery } from "@apollo/client/react";
import gql from "graphql-tag";

const QUERY = gql`
  query QuerySecurityInfo($isinCode: String!) {
    securityInfo(isinCode: $isinCode) {
      isinCode
      name
      currency
    }
  }
`;

interface SecurityInfoData {
  securityInfo: SecurityInfo;
}

/**
 * Custom hook to perform a GraphQL query to fetch information about a security.
 * @returns The result of the Apollo useQuery hook, providing loading state, error information,
 * and the data as `SecurityInfo`.
 */
export default function useQuerySecurityInfo(): useQuery.Result<SecurityInfoData> {
  const options = {
    fetchPolicy: "network-only" as const,
    client: LocalApolloClient,
  };

  return useQuery<SecurityInfoData>(QUERY, options);
}
