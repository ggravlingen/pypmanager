import {
  ApolloClient as _ApolloClient,
  ApolloLink,
  HttpLink,
  InMemoryCache,
} from "@apollo/client";
import {
  CombinedGraphQLErrors,
  CombinedProtocolErrors,
} from "@apollo/client/errors";
import { ErrorLink } from "@apollo/client/link/error";

// Define interfaces for better type safety
interface NetworkErrorWithStatus {
  statusCode?: number;
  status?: number;
  message?: string;
  response?: {
    status?: number;
  };
}

interface ExtensionsWithStatus {
  response?: {
    status?: number;
  };
  code?: number;
  status?: number;
  [key: string]: unknown;
}

/**
 * Error handling for network errors in Apollo Client.
 * If a network error occurs, this function checks the error type
 * and performs specific actions based on the error.
 * @param error - The error object from Apollo Client v4.
 * @returns Returns nothing.
 */
const _networkErrorLink = new ErrorLink(({ error, operation }) => {
  // Handle GraphQL errors using v4 API
  if (CombinedGraphQLErrors.is(error)) {
    error.errors.forEach(({ message, locations, path }) =>
      // eslint-disable-next-line no-console
      console.log(
        `[GraphQL error]: Message: ${message}, Location: ${locations}, Path: ${path}`,
      ),
    );
  }
  // Handle protocol errors using v4 API
  else if (CombinedProtocolErrors.is(error)) {
    error.errors.forEach(({ message, extensions }) => {
      // Check for HTTP status codes in protocol errors
      const typedExtensions = extensions as ExtensionsWithStatus;
      const statusCode =
        typedExtensions?.response?.status ||
        typedExtensions?.code ||
        typedExtensions?.status;

      if (statusCode === 401 || statusCode === 403) {
        // eslint-disable-next-line no-console
        console.warn("Apollo network error: Authentication issue", {
          errorMsg: message,
          statusCode,
        });
      } else {
        // eslint-disable-next-line no-console
        console.warn("Apollo protocol error", {
          errorMsg: message,
          extensions,
        });
      }
    });
  }
  // Handle other network errors
  else {
    // Check if it's a network error with status information
    const networkError = error as NetworkErrorWithStatus;
    if (networkError && typeof networkError === "object") {
      const statusCode =
        networkError.statusCode ||
        networkError.status ||
        networkError.response?.status;

      if (statusCode === 401 || statusCode === 403) {
        // eslint-disable-next-line no-console
        console.warn("Apollo network error: Authentication issue", {
          errorMsg: networkError.message || String(error),
          statusCode,
        });
      } else {
        // eslint-disable-next-line no-console
        console.warn("Apollo network error", {
          errorMsg: networkError.message || String(error),
          operation: operation.operationName,
        });
      }
    } else {
      // eslint-disable-next-line no-console
      console.warn("Apollo network error", {
        errorMsg: String(error),
        operation: operation.operationName,
      });
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
 * @returns The configured Apollo Client instance.
 */
const ApolloClient = new _ApolloClient({
  cache: new InMemoryCache(),
  link: ApolloLink.from([_networkErrorLink, _httpLink]),
});

export default ApolloClient;
