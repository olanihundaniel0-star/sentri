import puppeteer from 'puppeteer-core';
import { spawn } from 'child_process';
import http from 'http';

function checkUrl(url) {
  return new Promise((resolve) => {
    http.get(url, (res) => {
      resolve(res.statusCode);
    }).on('error', () => {
      resolve(null);
    });
  });
}

async function testServer(command, args, port, modeName) {
  console.log(`\n========================================`);
  console.log(`Testing Developer Console in ${modeName} (port ${port})...`);
  console.log(`========================================`);

  const process = spawn('npx', [command, ...args], {
    cwd: '/home/daniel/sentri/landing-page',
    stdio: 'ignore'
  });

  // Wait for server to start
  await new Promise((r) => setTimeout(r, 3000));

  const errors = [];
  const warnings = [];
  const failedRequests = [];
  const httpErrors = [];

  let browser;
  try {
    browser = await puppeteer.launch({
      executablePath: '/usr/bin/firefox',
      browser: 'firefox',
      headless: true,
      args: ['--window-size=1440,900']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 2 });

    // Console listeners
    page.on('console', (msg) => {
      const type = msg.type();
      const text = msg.text();
      if (type === 'error') {
        errors.push(`[Console Error] ${text}`);
      } else if (type === 'warning' || type === 'warn') {
        warnings.push(`[Console Warning] ${text}`);
      }
    });

    page.on('pageerror', (err) => {
      errors.push(`[Page Error] ${err.toString()}`);
    });

    page.on('requestfailed', (req) => {
      const failure = req.failure();
      failedRequests.push(`[Request Failed] ${req.url()} (${failure ? failure.errorText : 'failed'})`);
    });

    page.on('response', (res) => {
      const status = res.status();
      if (status >= 400) {
        httpErrors.push(`[HTTP ${status}] ${res.url()}`);
      }
    });

    const targetUrl = `http://localhost:${port}`;
    console.log(`Navigating to ${targetUrl}...`);
    await page.goto(targetUrl, { waitUntil: 'networkidle0', timeout: 15000 });

    // Scroll through page to trigger all sections, lazy elements, animations
    console.log('Scrolling page and testing interactive components...');
    const sections = ['#problem', '#how', '#action', '#infra', '#arch'];
    for (const sec of sections) {
      await page.evaluate((id) => {
        const el = document.querySelector(id);
        if (el) el.scrollIntoView({ behavior: 'instant', block: 'start' });
      }, sec);
      await new Promise((r) => setTimeout(r, 500));
    }
    await page.evaluate(() => window.scrollTo(0, 0));
    await new Promise((r) => setTimeout(r, 500));

    await browser.close();
  } catch (err) {
    errors.push(`[Test Execution Error] ${err.message}`);
  } finally {
    process.kill();
  }

  // Check direct favicon HTTP requests
  const faviconIcoStatus = await checkUrl(`http://localhost:${port}/favicon.ico`);
  const faviconSvgStatus = await checkUrl(`http://localhost:${port}/favicon.svg`);
  const faviconPngStatus = await checkUrl(`http://localhost:${port}/favicon.png`);

  console.log(`\nDirect Favicon Endpoint HTTP Statuses:`);
  console.log(`  - /favicon.ico -> ${faviconIcoStatus}`);
  console.log(`  - /favicon.svg -> ${faviconSvgStatus}`);
  console.log(`  - /favicon.png -> ${faviconPngStatus}`);

  console.log(`\nDeveloper Console & Network Results (${modeName}):`);
  console.log(`  - Console Errors: ${errors.length}`);
  if (errors.length > 0) errors.forEach(e => console.error(`    ${e}`));

  console.log(`  - Console Warnings: ${warnings.length}`);
  if (warnings.length > 0) warnings.forEach(w => console.warn(`    ${w}`));

  console.log(`  - Failed Requests: ${failedRequests.length}`);
  if (failedRequests.length > 0) failedRequests.forEach(f => console.error(`    ${f}`));

  console.log(`  - HTTP >= 400 Errors: ${httpErrors.length}`);
  if (httpErrors.length > 0) httpErrors.forEach(h => console.error(`    ${h}`));

  const isSuccess = errors.length === 0 && failedRequests.length === 0 && httpErrors.length === 0;
  console.log(`\nResult for ${modeName}: ${isSuccess ? 'PASSED ✅' : 'FAILED ❌'}`);
  return isSuccess;
}

async function main() {
  const previewSuccess = await testServer('vite', ['preview', '--port', '4173'], 4173, 'Production Preview');
  const devSuccess = await testServer('vite', ['--port', '5173'], 5173, 'Development Mode');

  if (!previewSuccess || !devSuccess) {
    console.error('\nDeveloper Console Test Suite Failed!');
    process.exit(1);
  } else {
    console.log('\nAll Developer Console Tests Passed Successfully! Everything renders cleanly without errors.');
    process.exit(0);
  }
}

main();
