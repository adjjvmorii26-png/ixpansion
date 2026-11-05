import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { setTimeout as delay } from "node:timers/promises";
import { readFile } from "node:fs/promises";
import { chromium } from "playwright";

const port = Number(process.env.HOLODECK_TEST_PORT || 4173);
const origin = `http://127.0.0.1:${port}`;
const server = spawn("python3", ["-m", "http.server", String(port), "--bind", "127.0.0.1"], {
  cwd: process.cwd(),
  stdio: "ignore"
});
let browser;

async function waitForServer() {
  for (let attempt = 0; attempt < 40; attempt++) {
    try {
      const response = await fetch(origin);
      if (response.ok) return;
    } catch {}
    await delay(250);
  }
  throw new Error("Holodeck static server did not start");
}

try {
  await waitForServer();
  browser = await chromium.launch({
    headless: true,
    args: [
      "--enable-webgl",
      "--use-gl=angle",
      "--use-angle=swiftshader",
      "--ignore-gpu-blocklist",
      "--disable-dev-shm-usage"
    ]
  });
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 }, acceptDownloads: true });
  const pageErrors = [];
  page.on("pageerror", error => pageErrors.push(error.message));

  await page.goto(`${origin}/holodeck/3d/`, { waitUntil: "domcontentloaded" });
  await page.waitForFunction(
    () => document.querySelector("#status")?.textContent.startsWith("tick=") ||
      document.querySelector("#err")?.textContent.length > 0,
    null,
    { timeout: 30000 }
  );
  assert.equal(await page.locator("#err").evaluate(el => getComputedStyle(el).display), "none",
    await page.locator("#err").textContent());
  assert.equal(await page.locator("#c").count(), 1);
  assert.equal(await page.locator("#targetFPS").inputValue(), "60");

  await page.locator("#targetFPS").selectOption("30");
  await page.waitForTimeout(800);
  const fps = Number(await page.locator("#fps").textContent());
  assert.ok(Number.isFinite(fps) && fps > 0, `invalid live FPS value: ${fps}`);
  assert.ok(Number(await page.locator("#frameIndex").textContent()) > 1);

  await page.locator("#pause").click();
  assert.equal(await page.locator("#pause").textContent(), "Resume");
  const pausedTick = Number(await page.locator("#simTicks").textContent());
  await page.waitForTimeout(250);
  assert.equal(Number(await page.locator("#simTicks").textContent()), pausedTick,
    "simulation tick advanced while paused");

  await page.locator("#step").click();
  assert.equal(Number(await page.locator("#simTicks").textContent()), pausedTick + 1,
    "single-step must advance exactly one simulation tick");

  await page.locator("#capture").click();
  await page.getByRole("button", { name: /Restore frame 1/ }).waitFor();
  assert.equal(await page.locator("#captureCount").textContent(), "(1/60)");
  assert.equal(await page.locator("#exportJPG").isEnabled(), true);

  await page.locator("#duplicate").click();
  await page.getByRole("button", { name: /Restore frame 2/ }).waitFor();
  assert.equal(await page.locator("#captureCount").textContent(), "(2/60)");

  await page.getByRole("button", { name: /Restore frame 1/ }).click();
  assert.equal(await page.getByRole("button", { name: /Restore frame 1/ }).getAttribute("aria-current"), "true");

  const jpgDownloadPromise = page.waitForEvent("download");
  await page.locator("#exportJPG").click();
  const jpgDownload = await jpgDownloadPromise;
  assert.match(jpgDownload.suggestedFilename(), /^holodeck-frame-1\.jpg$/);

  const jsonDownloadPromise = page.waitForEvent("download");
  await page.locator("#export").click();
  const jsonDownload = await jsonDownloadPromise;
  assert.equal(jsonDownload.suggestedFilename(), "ixpansion-holodeck-frames.json");
  const jsonPath = await jsonDownload.path();
  const exported = JSON.parse(await readFile(jsonPath, "utf8"));
  assert.equal(exported.format, "ixpansion-holodeck-frames");
  assert.equal(exported.captures.length, 2);
  assert.match(exported.captures[0].imageDataUrl, /^data:image\/jpeg;base64,/);

  await page.setViewportSize({ width: 390, height: 844 });
  assert.ok(await page.locator("#frameLab").evaluate(el => el.getBoundingClientRect().height > 0),
    "frame lab should remain visible at mobile width");
  assert.ok(await page.locator("#c").evaluate(el => el.getBoundingClientRect().width > 0),
    "canvas should remain visible at mobile width");

  assert.deepEqual(pageErrors, [], `browser page errors: ${pageErrors.join("; ")}`);
  console.log("Holodeck browser smoke: PASS");
  console.log("Verified: WebGL initialization, live FPS, pause, single-step, capture, duplicate, restore, JPG/JSON export, and mobile layout.");
} finally {
  if (browser) await browser.close();
  server.kill("SIGTERM");
}
