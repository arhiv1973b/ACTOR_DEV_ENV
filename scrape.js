const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto('https://share.gemini.google/bdpo1CWmSqzG', { waitUntil: 'networkidle' });
  
  // Wait a bit for client-side rendering
  await page.waitForTimeout(5000);
  
  const content = await page.content();
  console.log("--- PAGE CONTENT START ---");
  const text = await page.evaluate(() => document.body.innerText);
  console.log(text);
  console.log("--- PAGE CONTENT END ---");
  
  await browser.close();
})();
