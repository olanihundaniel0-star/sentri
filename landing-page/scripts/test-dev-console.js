import puppeteer from 'puppeteer-core';
import { spawn, execSync } from 'child_process';
import http from 'http';
import fs from 'fs';

function checkUrl(url) {
  return new Promise((resolve) => {
    http.get(url, (res) => {
      resolve(res.statusCode);
    }).on('error', () => {
      resolve(null);
    });
  });
}

async function runConsoleTest() {
  console.log('=====================================================');
  console.log('  LANDING PAGE DEVELOPER CONSOLE & FAVICON TEST SUITE');
  console.log('=====================================================\n');

  // 1. Build project
  console.log('[1/4] Building production landing page...');
  execSync('npm run build', { cwd: '/home/daniel/sentri/landing-page', stdio: 'inherit' });

  // 2. Start Vite preview server
  console.log('\n[2/4] Starting Vite preview server on port 4173...');
  const previewProcess = spawn('npx', ['vite', 'preview', '--port', '4173'], {
    cwd: '/home/daniel/sentri/landing-page',
    stdio: 'ignore'
  });

  await new Promise((resolve) => setTimeout(resolve, 2500));

  const consoleLogs = [];
  const consoleErrors = [];
  const consoleWarnings = [];
  const pageErrors = [];
  const failedRequests = [];
  const http404Errors = [];
  const allHttpErrors = [];

  let browser;
  try {
    console.log('\n[3/4] Launching headless browser & opening Developer Console listener...');

    const downloadedChrome = '/home/daniel/sentri/landing-page/chrome/linux-151.0.7922.71/chrome-linux64/chrome';
    let launchOptions;
    if (fs.existsSync(downloadedChrome)) {
      launchOptions = {
        executablePath: downloadedChrome,
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu', '--window-size=1440,900']
      };
    } else {
      launchOptions = {
        executablePath: '/usr/bin/firefox',
        browser: 'firefox',
        headless: true,
        args: ['--window-size=1440,900']
      };
    }

    browser = await puppeteer.launch(launchOptions);
    const page = await browser.newPage();
    await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 2 });

    // Developer Console Listeners
    page.on('console', (msg) => {
      const type = msg.type();
      const text = msg.text();
      const entry = `[${type.toUpperCase()}] ${text}`;
      consoleLogs.push(entry);

      if (type === 'error') {
        consoleErrors.push(text);
      } else if (type === 'warning' || type === 'warn') {
        consoleWarnings.push(text);
      }
    });

    page.on('pageerror', (err) => {
      pageErrors.push(err.toString());
    });

    page.on('requestfailed', (req) => {
      const failure = req.failure();
      const reason = failure ? failure.errorText : 'failed';
      failedRequests.push(`${req.url()} (${reason})`);
    });

    page.on('response', (res) => {
      const status = res.status();
      const url = res.url();
      if (status === 404) {
        http404Errors.push(url);
      } else if (status >= 400) {
        allHttpErrors.push(`HTTP ${status}: ${url}`);
      }
    });

    console.log('Navigating to http://localhost:4173 ...');
    await page.goto('http://localhost:4173', { waitUntil: 'networkidle0', timeout: 15000 });

    console.log('Interacting with sections to test layout rendering & dynamic components...');
    const selectors = ['header', '#problem', '#how', '#action', '#infra', '#arch'];
    for (const sel of selectors) {
      await page.evaluate((s) => {
        const el = document.querySelector(s);
        if (el) el.scrollIntoView({ behavior: 'instant', block: 'start' });
      }, sel);
      await new Promise((r) => setTimeout(r, 400));
    }

    // Scroll back to top
    await page.evaluate(() => window.scrollTo(0, 0));
    await new Promise((r) => setTimeout(r, 400));

    await browser.close();
  } catch (err) {
    console.error('Browser testing encountered an error:', err);
  } finally {
    previewProcess.kill();
  }

  // 4. Test direct favicon HTTP requests
  console.log('\n[4/4] Verifying Favicon Endpoints:');
  const faviconIco = await checkUrl('http://localhost:4173/favicon.ico');
  const faviconSvg = await checkUrl('http://localhost:4173/favicon.svg');
  const faviconPng = await checkUrl('http://localhost:4173/favicon.png');

  console.log(`  - GET /favicon.ico HTTP status: ${faviconIco}`);
  console.log(`  - GET /favicon.svg HTTP status: ${faviconSvg}`);
  console.log(`  - GET /favicon.png HTTP status: ${faviconPng}`);

  // Verify static files directly on disk in dist/
  const distIco = fs.existsSync('/home/daniel/sentri/landing-page/dist/favicon.ico');
  const distSvg = fs.existsSync('/home/daniel/sentri/landing-page/dist/favicon.svg');
  const distPng = fs.existsSync('/home/daniel/sentri/landing-page/dist/favicon.png');

  console.log(`  - dist/favicon.ico exists on disk: ${distIco ? 'YES ✅' : 'NO ❌'}`);
  console.log(`  - dist/favicon.svg exists on disk: ${distSvg ? 'YES ✅' : 'NO ❌'}`);
  console.log(`  - dist/favicon.png exists on disk: ${distPng ? 'YES ✅' : 'NO ❌'}`);

  console.log('\n=====================================================');
  console.log('                  TEST SUMMARY RESULTS               ');
  console.log('=====================================================');
  console.log(`- Total Console Messages Captured: ${consoleLogs.length}`);
  console.log(`- Console Errors: ${consoleErrors.length}`);
  if (consoleErrors.length > 0) consoleErrors.forEach((e) => console.log(`    ❌ ${e}`));

  console.log(`- Console Warnings: ${consoleWarnings.length}`);
  if (consoleWarnings.length > 0) consoleWarnings.forEach((w) => console.log(`    ⚠️ ${w}`));

  console.log(`- Uncaught Page Errors: ${pageErrors.length}`);
  if (pageErrors.length > 0) pageErrors.forEach((pe) => console.log(`    ❌ ${pe}`));

  console.log(`- Failed Network Requests: ${failedRequests.length}`);
  if (failedRequests.length > 0) failedRequests.forEach((fr) => console.log(`    ❌ ${fr}`));

  console.log(`- 404 Not Found Network Errors: ${http404Errors.length}`);
  if (http404Errors.length > 0) http404Errors.forEach((e404) => console.log(`    ❌ ${e404}`));

  const passed =
    distIco &&
    distSvg &&
    distPng &&
    consoleErrors.length === 0 &&
    pageErrors.length === 0 &&
    failedRequests.length === 0 &&
    http404Errors.length === 0;

  console.log('-----------------------------------------------------');
  if (passed) {
    console.log('🎉 ALL DEVELOPER CONSOLE TESTS PASSED CLEANLY! ZERO 404s & ERRORS.');
    process.exit(0);
  } else {
    console.error('❌ DEVELOPER CONSOLE TESTS FAILED. PLEASE REVIEW ERRORS ABOVE.');
    process.exit(1);
  }
}

runConsoleTest();
