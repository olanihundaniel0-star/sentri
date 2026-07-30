import puppeteer from 'puppeteer-core';
import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';

const outDir = '/home/daniel/sentri/docs/images';
if (!fs.existsSync(outDir)) {
  fs.mkdirSync(outDir, { recursive: true });
}

async function main() {
  const previewProcess = spawn('npx', ['vite', 'preview', '--port', '4173'], {
    cwd: '/home/daniel/sentri/landing-page',
    stdio: 'ignore'
  });

  await new Promise((r) => setTimeout(r, 2500));

  try {
    const browser = await puppeteer.launch({
      executablePath: '/usr/bin/firefox',
      browser: 'firefox',
      headless: true,
      args: ['--window-size=1440,900']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 2 });
    await page.goto('http://localhost:4173', { waitUntil: 'networkidle0' });

    const sections = [
      { id: null, selector: 'header', filename: 'sentri-hero.png', wait: 1000 },
      { id: 'problem', selector: '#problem', filename: 'sentri-problem.png', wait: 1200 },
      { id: 'how', selector: '#how', filename: 'sentri-how-it-works.png', wait: 1200 },
      { id: 'action', selector: '#action', filename: 'sentri-intervention.png', wait: 1200 },
      { id: 'infra', selector: '#infra', filename: 'sentri-infrastructure.png', wait: 1200 },
      { id: 'arch', selector: '#arch', filename: 'sentri-architecture.png', wait: 1200 }
    ];

    for (const sec of sections) {
      if (sec.id) {
        await page.evaluate((id) => {
          const el = document.getElementById(id);
          if (el) el.scrollIntoView({ behavior: 'instant', block: 'start' });
        }, sec.id);
      } else {
        await page.evaluate(() => window.scrollTo(0, 0));
      }

      await new Promise((r) => setTimeout(r, sec.wait));

      const element = await page.$(sec.selector);
      if (element) {
        await element.screenshot({
          path: path.join(outDir, sec.filename)
        });
        console.log(`Saved screenshot: ${sec.filename}`);
      }
    }

    await browser.close();
  } catch (err) {
    console.error('Error during screenshot capture:', err);
  } finally {
    previewProcess.kill();
  }
}

main();
