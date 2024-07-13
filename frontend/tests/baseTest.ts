import { expect, test as base } from "@playwright/test";
import * as fs from "fs";
import { graphql, http, RequestHandler } from "msw";
import * as path from "path";
import type { Config, MockServiceWorker } from "playwright-msw";
import { createWorkerFixture } from "playwright-msw";

const LOG_FOLDER_NAME = "logs";

const handlers: RequestHandler[] = [
  graphql.operation(({ query }) => {
    console.error(`
      Unhandled GraphQL operation:

      ${query}.
    `);
  }),
];

let isFileCleared = false;

const testFactory = (config?: Config) =>
  base.extend<{
    worker: MockServiceWorker;
    http: typeof http;
  }>({
    worker: createWorkerFixture(handlers, config),
    http,
    page: async ({ page }, use, testInfo) => {
      const fileName = testInfo.titlePath[0].replace(/[./-]/g, "_");
      page.on("console", async (msg) => {
        const filePath = `./${LOG_FOLDER_NAME}/${fileName}.log`;

        // If a folder was created, the path to the first created folder will be returned.
        fs.mkdirSync("./" + LOG_FOLDER_NAME, { recursive: true });

        // Clear the file
        if (!isFileCleared) {
          fs.writeFile(filePath, "", () => {
            isFileCleared = true;
          });
        }

        // Write log to file
        fs.appendFile(
          filePath,
          `${msg.type().toUpperCase()}:\n${msg.text()}\n\n`,
          () => {},
        );

        console.debug(
          "Wrote console log output to file:",
          path.resolve(filePath),
        );
      });

      await use(page);
    },
  });

const test = testFactory();

export { expect, test, testFactory };
