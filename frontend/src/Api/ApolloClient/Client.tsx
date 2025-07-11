import {
  ApolloClient as _ApolloClient,
  ApolloLink,
  HttpLink,
  InMemoryCache,
  type NormalizedCacheObject,
  type ServerError,
} from "@apollo/client";
import { type ErrorResponse, onError } from "@apollo/client/link/error";

/**
 * Error handling for network errors in Apollo Client.
 * If a network error occurs, this function checks the error status code
 * and performs specific actions based on the code.
 * @param networkError - The network error object.
 * @returns Returns nothing.
 */
const _networkErrorLink = onError(({ networkError }: ErrorResponse) => {
  if (networkError) {
    // Cast networkError to ServerError for more precise typing
    const netError = networkError as ServerError;
    if ("statusCode" in netError) {
      // Ensure statusCode exists on netError
      switch (netError.statusCode) {
        case 401:
        case 403:
          // Handle unauthorized or forbidden responses
          // eslint-disable-next-line no-console
          console.warn("Apollo network error: Authentication issue", {
            errorMsg: networkError.message,
          });
          break;
        default:
          // eslint-disable-next-line no-console
          console.warn("Apollo network error", {
            errorMsg: networkError.message,
          });
      }
    }
  }
});

/* 1. Build the URL from window.location */
const graphqlUri = new URL("./graphql", window.location.href).pathname;
// → "/api/hassio_ingress/<token>/graphql" in HA
// → "http://localhost:5173/graphql" in dev-server

const _httpLink = new HttpLink({
  uri: graphqlUri,
  credentials: "same-origin",
});

/**
 * Initializes and configures the Apollo Client instance.
 *
 * This Apollo Client is configured with an in-memory cache and a composite link
 * that includes both error handling and HTTP communication functionalities.
 * The `_networkErrorLink` handles network errors globally, while the `_httpLink`
 * manages HTTP requests to the GraphQL server.
 * @returns {_ApolloClient<NormalizedCacheObject>} The configured Apollo Client instance.
 */
const ApolloClient: _ApolloClient<NormalizedCacheObject> = new _ApolloClient({
  cache: new InMemoryCache(),
  link: ApolloLink.from([_networkErrorLink, _httpLink]),
});

export default ApolloClient;
