import type { PlaywrightTestConfig } from "@playwright/test";
import { devices } from "@playwright/test";

import dotenv from "dotenv";

dotenv.config();

const isUpdateSnapshots = process.argv.includes("--update-snapshots");
const RES = { width: 1920, height: 1080 };

if (isUpdateSnapshots) {
  console.log("Running config with updating snapshots settings");
}

/**
 * See https://playwright.dev/docs/test-configuration.
 */
const config: PlaywrightTestConfig = {
  testDir: "./tests/test-files/",
  testMatch: /.*\.ts/,
  updateSnapshots: isUpdateSnapshots ? "all" : "none",
  snapshotPathTemplate:
    "./tests/__screenshots__{/projectName}/{testFilePath}/{testName}/{arg}{ext}",
  /* Maximum time one test can run for. */
  timeout: 30 * 1000,
  expect: {
    /**
     * Maximum time expect() should wait for the condition to be met.
     * For example in `await expect(locator).toHaveText();`
     */
    timeout: 5000,
    toHaveScreenshot: {
      // an acceptable amount of pixels that could be different, unset by default.
      maxDiffPixels: isUpdateSnapshots ? 0 : 800,
    },
  },
  /* Run tests in files in parallel */
  fullyParallel: true,
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  /* No need to run retries */
  retries: 0,
  /*
    Reporter to use. See https://playwright.dev/docs/test-reporters
    Uses dot in CI/CD
  */
  reporter: [["html", { outputFolder: "html-report" }]],

  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    headless: true,

    // Emulates the user timezone.
    timezoneId: "Europe/Stockholm",
    viewport: RES, // Explicitly define the viewport size

    /* Maximum time each action such as `click()` can take. Defaults to 0 (no limit). */
    actionTimeout: 0,

    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: "http://localhost:3000",

    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: "on-first-retry",
  },
  /* Configure projects for major browsers */
  projects: [
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        viewport: RES, // Explicit viewport dimensions
        deviceScaleFactor: undefined,
        hasTouch: undefined,
        isMobile: undefined,
      },
    },
  ],

  /* Folder for test artifacts such as screenshots, videos, traces, etc. */
  outputDir: "test-results/",
};

export default config;
