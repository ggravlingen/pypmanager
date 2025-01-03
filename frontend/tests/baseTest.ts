import { expect, test as base } from "@playwright/test";
import * as fs from "fs";
import { graphql, http, RequestHandler } from "msw";
import * as path from "path";
import type { Config, MockServiceWorker } from "playwright-msw";
import { createWorkerFixture } from "playwright-msw";

const LOG_FOLDER_NAME = "logs";

const handlers: RequestHandler[] = [
  graphql.operation(({ query }) => {
    // eslint-disable-next-line no-console
    console.error(`
      Unhandled GraphQL operation:

      ${query}.
    `);
  }),
];

let isFileCleared = false;

const filterStrings = ["Download the React DevTools"];

const testFactory = (config?: Config) =>
  base.extend<{
    worker: MockServiceWorker;
    http: typeof http;
  }>({
    worker: createWorkerFixture(handlers, config),
    http,
    page: async ({ page }, use, testInfo) => {
      // Set the current time to 2024-12-31 10:00:00 to avoid issues with
      // date-based tests
      await page.clock.setFixedTime(new Date("2024-12-31T10:00:00"));

      const fileName = testInfo.titlePath[0].replace(/[./-]/g, "_");
      page.on("console", async (msg) => {
        const filePath = `./${LOG_FOLDER_NAME}/${fileName}.log`;

        // Clear the file
        if (!isFileCleared) {
          fs.writeFile(filePath, "", () => {
            isFileCleared = true;
          });
        }

        // Filter out specific log messages
        if (
          filterStrings.some((filterString) =>
            msg.text().includes(filterString),
          )
        ) {
          return; // Skip this log message
        }

        // If a folder was created, the path to the first created folder will be returned.
        fs.mkdirSync("./" + LOG_FOLDER_NAME, { recursive: true });

        // Write log to file
        fs.appendFile(
          filePath,
          `${msg.type().toUpperCase()}:\n${msg.text()}\n\n`,
          () => {},
        );

        // eslint-disable-next-line no-console
        console.debug(
          "Wrote console log output to file:",
          path.resolve(filePath),
        );
      });

      /* eslint-disable react-hooks/rules-of-hooks */
      await use(page);
    },
  });

const test = testFactory();

export { expect, test, testFactory };
