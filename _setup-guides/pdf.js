// Renders a guide HTML file to an A4 PDF with Playwright (used by build.py).
let chromium;
try { ({ chromium } = require('playwright')); } catch { ({ chromium } = require('/usr/local/lib/node_modules/playwright')); }
const [src, out] = process.argv.slice(2);
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + src, { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: out, format: 'A4', printBackground: true, preferCSSPageSize: true });
  await b.close();
})();
