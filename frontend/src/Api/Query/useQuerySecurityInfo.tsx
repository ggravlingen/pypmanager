import { LocalApolloClient, SecurityInfo } from "@Api";
import { QueryHookOptions, QueryResult, useQuery } from "@apollo/client";
import gql from "graphql-tag";

const QUERY = gql`
  query QuerySecurityInfo($isinCode: String!) {
    securityInfo(isinCode: $isinCode) {
      isinCode
      name
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
export default function useQuerySecurityInfo(): QueryResult<SecurityInfoData> {
  const options: QueryHookOptions<SecurityInfoData> = {
    fetchPolicy: "network-only",
    client: LocalApolloClient,
  };

  return useQuery<SecurityInfoData>(QUERY, options);
}
