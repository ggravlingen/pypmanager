import { NavigationBar, TableGeneralLedger } from "./components";
import React from "react";

export default function MainLayout() {
  return (
    <div style={{ display: "flex" }}>
      <NavigationBar />
      <div style={{ flexGrow: 1 }}>
        <TableGeneralLedger />
      </div>
    </div>
  );
}
