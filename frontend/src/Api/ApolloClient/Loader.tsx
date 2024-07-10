import { Box,Skeleton } from "@mui/material";
import React from "react";

/**
 * Interface for QueryLoader component props.
 * loading - Indicates if the query is currently loading.
 * data - The data returned from the query. This can be any type, depending on the query.
 * [error] - An optional error object that may be returned from the query.
 * children - React children that are rendered when the query is not loading and no error has occurred.
 */
interface QueryLoaderProps {
  loading: boolean;
  // Data can be anything
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  data: any;
  error?: Error;
  children: React.ReactNode;
}

/**
 * Renders content based on the loading state, error presence, or data availability.
 * This component is designed to handle the rendering logic for asynchronous data fetching operations.
 * It displays a loading indicator when data is being fetched, an error message if the fetch fails,
 * a message indicating no data is available if the result is empty, and the children components
 * when data is successfully fetched without errors.
 * @param props - The properties passed to the QueryLoader component.
 * @param props.loading - Indicates if the data is currently being loaded.
 * @param props.data - The data fetched from the query. Can be of any type.
 * @param [props.error] - An optional error object if the query failed.
 * @param props.children - The content to render when data is successfully fetched.
 * @returns The rendered element based on the current state (loading, error, no data, or success).
 */
export default function QueryLoader({
  loading,
  data,
  error,
  children,
}: QueryLoaderProps): JSX.Element {
  if (loading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
        }}
      >
        <Skeleton width={150} height={150} />
      </Box>
    );
  }

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  if (!data) {
    return <div>No data available.</div>;
  }

  return <>{children}</>;
}
