/* eslint-disable @typescript-eslint/no-unused-vars */
import { graphql, HttpResponse } from "msw";

import { expect, test } from "../baseTest.ts";

const TransactionList = {
  allTransaction: [
    {
      transactionDate: new Date("2021-06-01"),
      broker: "IBKR",
      source: "IBKR",
      action: "BUY",
      name: "ABCD",
      noTraded: 10,
      commission: 0,
      fx: 1.22,
      price: 120,
      currency: "USD",
      cashFlow: 1200,
      costBaseAverage: 120,
      quantityHeld: 10,
      pnlTotal: null,
      pnlTrade: null,
      pnlDividend: null,
    },
    {
      transactionDate: new Date("2024-05-01"),
      broker: "IBKR",
      source: "IBKR",
      action: "SELL",
      name: "EFGH",
      noTraded: 10,
      commission: 0,
      fx: 1.22,
      price: 120,
      currency: "USD",
      cashFlow: 1200,
      costBaseAverage: 120,
      quantityHeld: null,
      pnlTotal: 1.0,
      pnlTrade: 0.5,
      pnlDividend: 0.5,
    },
  ],
};

test.describe.parallel("Test views", () => {
  test("Test loading the transaction table", async ({ page, worker }) => {
    await worker.use(
      graphql.query("QueryAllTransaction", ({ query, variables }) => {
        console.log("Intercepted QueryAllTransaction");
        return HttpResponse.json({
          data: TransactionList,
        });
      }),
    );

    await page.goto("/#/transaction");
    await page.waitForTimeout(2000);

    await expect(page).toHaveScreenshot("1.png");
  });
});
