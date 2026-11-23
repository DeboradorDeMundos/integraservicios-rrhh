/**
 * Export slide-deck HTML (one .on slide at a time) to multi-page PDF.
 * Usage: node export-html-to-pdf.mjs <input.html> [output.pdf]
 */
import { chromium } from "playwright";
import { pathToFileURL } from "url";
import path from "path";
import fs from "fs";

const htmlArg = process.argv[2];
if (!htmlArg) {
  console.error("Usage: node export-html-to-pdf.mjs <input.html> [output.pdf]");
  process.exit(1);
}

const htmlPath = path.resolve(htmlArg);
if (!fs.existsSync(htmlPath)) {
  console.error("File not found:", htmlPath);
  process.exit(1);
}

const pdfPath =
  process.argv[3] || htmlPath.replace(/\.html?$/i, "") + ".pdf";

const PRINT_CSS = `
  html, body {
    overflow: visible !important;
    height: auto !important;
  }
  body.pdf-export .deck {
    height: auto !important;
    overflow: visible !important;
  }
  body.pdf-export .slide {
    display: flex !important;
    flex-direction: column;
    justify-content: center;
    box-sizing: border-box;
    width: 100% !important;
    min-height: 1080px;
    height: 1080px;
    page-break-after: always;
    break-after: page;
    overflow: hidden;
  }
  body.pdf-export .slide:last-child {
    page-break-after: auto;
    break-after: auto;
  }
  body.pdf-export .nav,
  body.pdf-export .hud,
  body.pdf-export .cursor,
  body.pdf-export .notes,
  body.pdf-export .notes-fab,
  body.pdf-export .progress,
  body.pdf-export #net,
  body.pdf-export .vignette,
  body.pdf-export .flash,
  body.pdf-export .recording-mode .presenter-hint {
    display: none !important;
  }
  * {
    animation: none !important;
    transition: none !important;
  }
`;

const browser = await chromium.launch();
const page = await browser.newPage({
  viewport: { width: 1920, height: 1080 },
  deviceScaleFactor: 1,
});

await page.goto(pathToFileURL(htmlPath).href, {
  waitUntil: "networkidle",
  timeout: 120_000,
});

await page.waitForSelector(".deck .slide", { timeout: 30_000 });
await page.waitForTimeout(1500);

await page.addStyleTag({ content: PRINT_CSS });
await page.evaluate(() => {
  document.body.classList.add("pdf-export");
  document.querySelectorAll(".slide").forEach((s) => s.classList.add("on"));
});

await page.emulateMedia({ media: "print" });

const slideCount = await page.locator(".slide").count();
console.log(`Exporting ${slideCount} slides → ${pdfPath}`);

await page.pdf({
  path: pdfPath,
  width: "1920px",
  height: "1080px",
  printBackground: true,
  margin: { top: 0, right: 0, bottom: 0, left: 0 },
});

await browser.close();
console.log("Done:", pdfPath);
