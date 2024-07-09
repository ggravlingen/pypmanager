import { useQueryGetLedger } from "@Api";
import React from "react";

export default function App(): JSX.Element {
  const { data, error, loading } = useQueryGetLedger();

  console.log(loading);
  console.log(error);
  console.log(data);

  return <div>testar</div>;
}
