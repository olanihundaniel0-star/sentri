import puppeteer from 'puppeteer-core';
import fs from 'fs';

async function testMermaid() {
  const readme = fs.readFileSync('/home/daniel/sentri/README.md', 'utf8');
  const regex = /```mermaid\n([\s\S]*?)\n```/g;
  const blocks = [];
  let match;
  while ((match = regex.exec(readme)) !== null) {
    blocks.push(match[1]);
  }

  console.log(`Found ${blocks.length} Mermaid blocks in README.md.`);

  const chromePath = '/home/daniel/sentri/landing-page/chrome/linux-151.0.7922.71/chrome-linux64/chrome';
  const browser = await puppeteer.launch({
    executablePath: '/usr/bin/firefox',
    browser: 'firefox',
    headless: true
  });

  const page = await browser.newPage();
  
  // HTML with Mermaid JS loaded
  const htmlContent = `
    <!DOCTYPE html>
    <html>
    <head>
      <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    </head>
    <body>
      <script>
        mermaid.initialize({ startOnLoad: false });
      </script>
    </body>
    </html>
  `;

  await page.setContent(htmlContent);

  for (let i = 0; i < blocks.length; i++) {
    const code = blocks[i];
    const result = await page.evaluate(async (mermaidCode, index) => {
      try {
        const valid = await mermaid.parse(mermaidCode);
        return { index, success: true, valid };
      } catch (err) {
        return { index, success: false, error: err.str || err.message || String(err) };
      }
    }, code, i + 1);

    if (result.success) {
      console.log(`✅ Diagram ${result.index}: Valid!`);
    } else {
      console.error(`❌ Diagram ${result.index}: FAILED!`);
      console.error(`   Error details:`, result.error);
    }
  }

  await browser.close();
}

testMermaid();
