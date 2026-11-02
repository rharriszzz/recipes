// Capture the current local build, without relying on the deployed site's revision.
import { execFileSync, spawn } from 'node:child_process';
import { once } from 'node:events';
import { mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const root = fileURLToPath(new URL('../', import.meta.url));
execFileSync('python3', ['scripts/build.py'], { cwd: root, stdio: 'inherit' });

// Port 0 lets the OS choose a free port; reuse the production-path preview server.
const server = spawn('python3', ['scripts/preview.py', '--port', '0'], {
  cwd: root,
  stdio: ['ignore', 'pipe', 'inherit'],
});
let browser;
try {
  const url = await new Promise((resolve, reject) => {
    let output = '';
    const timeout = setTimeout(() => reject(new Error('Preview startup timed out')), 10_000);
    const finish = (error, value) => {
      clearTimeout(timeout);
      if (error) reject(error);
      else resolve(value);
    };
    server.once('error', error => finish(error));
    server.once('exit', code => finish(new Error(`Preview exited with code ${code}`)));
    server.stdout.on('data', chunk => {
      output += chunk;
      const match = output.match(/Recipe preview: (http:\/\/127\.0\.0\.1:\d+\/recipes\/)/);
      if (match) finish(null, match[1]);
    });
  });
  browser = await chromium.launch();
  const page = await browser.newPage({
    viewport: { width: 1280, height: 900 },
    deviceScaleFactor: 2,
    colorScheme: 'light',
    reducedMotion: 'reduce',
    locale: 'en-US',
    timezoneId: 'UTC',
  });
  const failures = [];
  page.on('pageerror', error => failures.push(error.message));
  page.on('requestfailed', request => failures.push(`Failed request: ${request.url()}`));
  page.on('response', response => {
    if (!response.ok()) failures.push(`HTTP ${response.status()}: ${response.url()}`);
  });
  await page.goto(url, { waitUntil: 'load' });
  const main = page.locator('main.simple-index');
  await main.locator('h1').waitFor({ state: 'visible' });
  await main.locator('.simple-recipe-list a').last().waitFor({ state: 'visible' });
  await page.evaluate(() => document.fonts.ready);

  // The main element is 900px wide, while its text occupies only the left side.
  // Measure actual text rather than block boxes to exclude the empty right side.
  // Include every recipe and a small paper inset; no fixed titles or item count.
  const clip = await main.evaluate(element => {
    const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
    const rects = [];
    while (walker.nextNode()) {
      if (!walker.currentNode.textContent.trim()) continue;
      const range = document.createRange();
      range.selectNodeContents(walker.currentNode);
      rects.push(...[...range.getClientRects()].filter(rect => rect.width && rect.height));
    }
    if (!rects.length) throw new Error('Homepage has no visible content');
    const inset = 16;
    const x = Math.max(0, Math.floor(Math.min(...rects.map(rect => rect.left))) - inset);
    const y = Math.max(0, Math.floor(Math.min(...rects.map(rect => rect.top))) - inset);
    const right = Math.ceil(Math.max(...rects.map(rect => rect.right))) + inset;
    const bottom = Math.ceil(Math.max(...rects.map(rect => rect.bottom))) + inset;
    return { x, y, width: right - x, height: bottom - y };
  });
  if (failures.length) throw new Error(failures.join('\n'));
  // Keep the full list inside the capture viewport as more recipes are added.
  if (clip.y + clip.height > page.viewportSize().height) {
    await page.setViewportSize({ width: 1280, height: Math.ceil(clip.y + clip.height) });
  }
  await mkdir(new URL('../images/', import.meta.url), { recursive: true });
  const path = fileURLToPath(new URL('../images/homepage-card.png', import.meta.url));
  await page.screenshot({ path, clip, animations: 'disabled', caret: 'hide' });
  console.log(`Saved images/homepage-card.png (${clip.width} × ${clip.height} CSS pixels at 2×)`);
} finally {
  await browser?.close();
  if (server.exitCode === null && server.signalCode === null) {
    const exited = once(server, 'exit');
    server.kill();
    await exited;
  }
}
