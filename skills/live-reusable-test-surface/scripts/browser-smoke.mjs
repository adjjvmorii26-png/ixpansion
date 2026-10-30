#!/usr/bin/env node
/**
 * Evidence-first browser smoke runner.
 *
 * Requires Playwright to be installed in the consuming project:
 *   npm install --save-dev playwright
 *   npx playwright install chromium
 *
 * Example:
 *   node skills/live-reusable-test-surface/scripts/browser-smoke.mjs \
 *     https://example.com --out artifacts/browser-smoke --expect-title "Example Domain"
 */
import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { pathToFileURL } from "node:url";

function usage() {
  console.log(`Usage:
  node browser-smoke.mjs <http(s)-url> [options]

Options:
  --out <directory>       Evidence output directory (default: artifacts/browser-smoke)
  --viewport <WxH>        Viewport (default: 1280x800; e.g. 390x844)
  --timeout <ms>          Navigation timeout (default: 20000)
  --expect-title <text>   Require page title to contain this text
  --expect-text <text>    Require visible page body text to contain this text
  --help                  Show this help

Exit codes:
  0 = assertions passed (or observation-only run completed without a hard failure)
  1 = navigation, browser, or supplied assertion failure
  2 = invalid arguments or missing Playwright dependency

Observation-only runs are reported as REVIEW, never PASS. A rendered page alone is not proof of correctness.`);
}

function parseArgs(argv) {
  const result = {
    url: "",
    out: "artifacts/browser-smoke",
    viewport: "1280x800",
    timeout: 20000,
    expectTitle: null,
    expectText: null,
  };
  const args = [...argv];
  while (args.length) {
    const item = args.shift();
    if (item === "--help") { result.help = true; continue; }
    if (item === "--out" || item === "--viewport" || item === "--timeout" ||
        item === "--expect-title" || item === "--expect-text") {
      const value = args.shift();
      if (!value || value.startsWith("--")) throw new Error(`Missing value for ${item}`);
      if (item === "--out") result.out = value;
      if (item === "--viewport") result.viewport = value;
      if (item === "--timeout") result.timeout = Number(value);
      if (item === "--expect-title") result.expectTitle = value;
      if (item === "--expect-text") result.expectText = value;
      continue;
    }
    if (item.startsWith("--")) throw new Error(`Unknown option: ${item}`);
    if (result.url) throw new Error("Only one target URL is accepted");
    result.url = item;
  }
  if (result.help) return result;
  let parsed;
  try { parsed = new URL(result.url); } catch { throw new Error("A valid target URL is required"); }
  if (!["http:", "https:"].includes(parsed.protocol)) throw new Error("Only HTTP and HTTPS targets are allowed");
  if (!/^\d{2,5}x\d{2,5}$/.test(result.viewport)) throw new Error("Viewport must use WIDTHxHEIGHT, for example 1280x800");
  const [width, height] = result.viewport.split("x").map(Number);
  if (width < 200 || width > 5000 || height < 200 || height > 5000) throw new Error("Viewport dimensions must be between 200 and 5000 pixels");
  result.width = width;
  result.height = height;
  if (!Number.isInteger(result.timeout) || result.timeout < 1000 || result.timeout > 120000) throw new Error("Timeout must be an integer between 1000 and 120000 ms");
  result.url = parsed.href;
  return result;
}

function isoNow() { return new Date().toISOString(); }

async function main() {
  let options;
  try {
    options = parseArgs(process.argv.slice(2));
    if (options.help) { usage(); return 0; }
  } catch (error) {
    console.error(`Argument error: ${error.message}`);
    usage();
    return 2;
  }

  let chromium;
  try {
    ({ chromium } = await import("playwright"));
  } catch {
    console.error("Playwright is not installed. Run: npm install --save-dev playwright && npx playwright install chromium");
    return 2;
  }

  const outputDir = path.resolve(options.out);
  await fs.mkdir(outputDir, { recursive: true });
  const stamp = new Date().toISOString().replace(/[:.]/g, "-");
  const screenshotPath = path.join(outputDir, `browser-smoke-${stamp}.png`);
  const reportPath = path.join(outputDir, `browser-smoke-${stamp}.json`);
  const report = {
    schema_version: "1.0",
    started_at: isoNow(),
    target_url: options.url,
    viewport: { width: options.width, height: options.height },
    timeout_ms: options.timeout,
    assertions: {
      expected_title_contains: options.expectTitle,
      expected_text_contains: options.expectText,
    },
    page_title: null,
    final_url: null,
    main_document_status: null,
    console_errors: [],
    page_errors: [],
    failed_requests: [],
    http_error_responses: [],
    assertions_results: [],
    screenshot: screenshotPath,
    result: "REVIEW",
    failure_reason: null,
    finished_at: null,
  };

  let browser;
  try {
    browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
      viewport: { width: options.width, height: options.height },
      ignoreHTTPSErrors: false,
    });
    const page = await context.newPage();
    page.setDefaultTimeout(options.timeout);
    page.on("console", message => {
      if (message.type() === "error") report.console_errors.push({ text: message.text(), at: isoNow() });
    });
    page.on("pageerror", error => report.page_errors.push({ message: error.message, at: isoNow() }));
    page.on("requestfailed", request => {
      report.failed_requests.push({
        url: request.url(),
        method: request.method(),
        error: request.failure()?.errorText ?? "unknown",
        at: isoNow(),
      });
    });
    page.on("response", response => {
      if (response.status() >= 400) {
        report.http_error_responses.push({ url: response.url(), status: response.status(), at: isoNow() });
      }
    });

    try {
      const response = await page.goto(options.url, { waitUntil: "domcontentloaded", timeout: options.timeout });
      report.main_document_status = response?.status() ?? null;
    } catch (error) {
      report.failure_reason = `Navigation failed: ${error.message}`;
    }

    report.final_url = page.url();
    try { report.page_title = await page.title(); } catch (error) {
      report.failure_reason ??= `Could not read page title: ${error.message}`;
    }

    if (options.expectTitle !== null) {
      const passed = (report.page_title ?? "").includes(options.expectTitle);
      report.assertions_results.push({ assertion: "title_contains", expected: options.expectTitle, actual: report.page_title, passed });
    }
    if (options.expectText !== null) {
      let bodyText = "";
      try { bodyText = await page.locator("body").innerText(); } catch {}
      const passed = bodyText.includes(options.expectText);
      report.assertions_results.push({ assertion: "body_text_contains", expected: options.expectText, passed });
    }

    try {
      await page.screenshot({ path: screenshotPath, fullPage: true, animations: "disabled", timeout: options.timeout });
    } catch (error) {
      report.failure_reason ??= `Screenshot failed: ${error.message}`;
    }

    const assertionsProvided = options.expectTitle !== null || options.expectText !== null;
    const assertionsPassed = report.assertions_results.every(item => item.passed);
    const hardFailure = Boolean(report.failure_reason) ||
      (report.main_document_status !== null && report.main_document_status >= 400) ||
      report.page_errors.length > 0;
    report.result = hardFailure || !assertionsPassed ? "FAIL" : (assertionsProvided ? "PASS" : "REVIEW");
    if (!report.failure_reason && report.main_document_status !== null && report.main_document_status >= 400) {
      report.failure_reason = `Main document returned HTTP ${report.main_document_status}`;
    }
    if (!report.failure_reason && report.page_errors.length) {
      report.failure_reason = `${report.page_errors.length} uncaught page error(s) observed`;
    }
    report.finished_at = isoNow();
    await fs.writeFile(reportPath, JSON.stringify(report, null, 2) + "\n", "utf8");
    console.log(JSON.stringify({
      result: report.result,
      target_url: report.target_url,
      page_title: report.page_title,
      main_document_status: report.main_document_status,
      page_errors: report.page_errors.length,
      console_errors: report.console_errors.length,
      failed_requests: report.failed_requests.length,
      http_error_responses: report.http_error_responses.length,
      screenshot: screenshotPath,
      report: reportPath,
      failure_reason: report.failure_reason,
    }, null, 2));
    await context.close();
    return report.result === "FAIL" ? 1 : 0;
  } catch (error) {
    report.failure_reason = error.message;
    report.result = "FAIL";
    report.finished_at = isoNow();
    await fs.writeFile(reportPath, JSON.stringify(report, null, 2) + "\n", "utf8");
    console.error(`Browser run failed. Evidence report: ${reportPath}\n${error.stack ?? error.message}`);
    return 1;
  } finally {
    if (browser) await browser.close().catch(() => {});
  }
}

main().then(code => { process.exitCode = code; });
