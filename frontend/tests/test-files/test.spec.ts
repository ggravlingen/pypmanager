/* eslint-disable @typescript-eslint/no-unused-vars */
import { graphql, HttpResponse } from "msw";

import { expect, test } from "../baseTest.ts";

const QueryCurrentPortfolio = {
  currentPortfolio: [
    {
      name: "Test Fund 1",
      isinCode: "SE0013720000",
      investedAmount: 1000,
      currentMarketValueAmount: 2000,
      pnlTotal: 1000,
      pnlRealized: 500,
      pnlUnrealized: 500,
      marketValueDate: "2024-12-23",
      marketValuePrice: 200,
    },
    {
      name: "Security A, Inc",
      isinCode: "SE0013720001",
      investedAmount: 1000,
      currentMarketValueAmount: 2000,
      pnlTotal: 1000,
      pnlRealized: 500,
      pnlUnrealized: 500,
      marketValueDate: "2024-12-23",
      marketValuePrice: 200,
    },
  ],
}

const QueryMarketDataOverviewData = {
  marketDataOverview: [
    {
      name: "Test Fund 1",
      isinCode: "SE0013720000",
      firstDate: "2020-03-06",
      lastDate: "2024-12-23",
      currency: "SEK",
    },
  ],
};

const ResultStatementData = {
  resultStatement: [
    {
      itemName: "calc_pnl_transaction_dividend",
      yearList: [
        2006, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024,
      ],
      amountList: [
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        100,
        200,
      ],
      isTotal: false,
    },
    {
      itemName: "calc_pnl_transaction_trade",
      yearList: [
        2006, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024,
      ],
      amountList: [
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        3000,
        4000,
      ],
      isTotal: false,
    },
    {
      itemName: "calc_pnl_transaction_total",
      yearList: [
        2006, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024,
      ],
      amountList: [
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        3100,
        4200,
      ],
      isTotal: true,
    },
  ],
};

const TransactionList = {
  allTransaction: [
    {
      transactionDate: new Date("2021-06-01"),
      isinCode: "abc123",
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
      isinCode: "abc123",
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

    await page.mouse.move(100, 100);

    await expect(page).toHaveScreenshot("1.png");
  });

  test("Test loading the income statement table", async ({ page, worker }) => {
    await worker.use(
      graphql.query("QueryResultStatement", ({ query, variables }) => {
        console.log("Intercepted QueryResultStatement");
        return HttpResponse.json({
          data: ResultStatementData,
        });
      }),
    );

    await page.goto("/#/income_statement");
    await page.waitForTimeout(2000);

    await page.mouse.move(100, 100);

    await expect(page).toHaveScreenshot("1.png");
  });

  test("Test loading the market data overview table", async ({
    page,
    worker,
  }) => {
    await worker.use(
      graphql.query("QueryMarketDataOverview", ({ query, variables }) => {
        console.log("Intercepted QueryMarketDataOverview");
        return HttpResponse.json({
          data: QueryMarketDataOverviewData,
        });
      }),
    );

    await page.goto("/#/marketDataOverview");
    await page.waitForTimeout(2000);

    await page.mouse.move(100, 100);

    await expect(page).toHaveScreenshot("1.png");
  });

  test("Test loading current portfolio table", async ({
    page,
    worker,
  }) => {
    await worker.use(
      graphql.query("QueryCurrentPortfolio", ({ query, variables }) => {
        console.log("Intercepted QueryCurrentPortfolio");
        return HttpResponse.json({
          data: QueryCurrentPortfolio,
        });
      }),
    );

    await page.goto("/#/");
    await page.waitForTimeout(2000);

    await page.mouse.move(100, 100);

    await expect(page).toHaveScreenshot("1.png");
  });
});
