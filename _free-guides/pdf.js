// A4 PDF with a running header and page numbers (build.py).
let chromium; try { ({ chromium } = require('playwright')); } catch { ({ chromium } = require('/usr/local/lib/node_modules/playwright')); }
const [src, out, title] = process.argv.slice(2);
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + src, { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready);
  const f = 'font-family:Arial,sans-serif;font-size:7.5pt;color:#62605D;width:100%;padding:0 15mm;display:flex;justify-content:space-between';
  await p.pdf({ path: out, format: 'A4', printBackground: true, displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate: `<div style="${f}"><span>Totality 360 · ${title}</span><span><span class="pageNumber"></span></span></div>`,
    margin: { top: '16mm', bottom: '16mm', left: '0', right: '0' } });
  await b.close();
})();
