import React from "react";

interface QueryLoaderProps {
  loading: boolean;
  data: any;
  error?: Error;
  children: React.ReactNode;
}

export default function QueryLoader({
  loading,
  data,
  error,
  children,
}: QueryLoaderProps): JSX.Element {
  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  if (!data) {
    return <div>No data available.</div>;
  }

  return <>{children}</>;
}
