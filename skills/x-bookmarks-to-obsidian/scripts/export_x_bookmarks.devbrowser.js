const page = await browser.getPage("x-bookmarks-to-obsidian-export");
let knownLinks = new Set();

try {
  const knownRaw = await readFile("x-bookmarks-to-obsidian-known.json");
  const parsed = JSON.parse(knownRaw);
  if (Array.isArray(parsed)) {
    knownLinks = new Set(parsed.filter((item) => typeof item === "string" && item.length > 0));
  }
} catch {}

await page.goto("https://x.com/i/bookmarks");
await page.waitForTimeout(5000);
await page.evaluate(() => window.scrollTo(0, 0));
await page.waitForTimeout(1500);

const collected = new Map();
let sameCount = 0;
let lastSize = 0;
let knownBatchCount = 0;
let stopReason = "max-steps";
let lastProgressAt = 0;

function logProgress(step, itemsInView, knownMatches, note = "") {
  const payload = {
    phase: "export",
    step: step + 1,
    collected: collected.size,
    itemsInView,
    knownMatches,
    knownBatches: knownBatchCount,
    stagnantSteps: sameCount,
  };
  if (note) {
    payload.note = note;
  }
  console.log(JSON.stringify(payload));
}

for (let step = 0; step < 500; step += 1) {
  const items = await page.evaluate(() => {
    return Array.from(document.querySelectorAll("article"))
      .map((article) => {
        const links = Array.from(article.querySelectorAll("a[href]"))
          .map((anchor) => anchor.href)
          .filter(Boolean);
        const statusLink = links.find((href) => /\/status\/\d+/.test(href)) || null;
        const text = (article.innerText || "").trim();
        const lines = text
          .split("\n")
          .map((segment) => segment.trim())
          .filter(Boolean);
        const handle = lines.find((line) => line.startsWith("@")) || "";
        const time =
          lines.find((line) =>
            /^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d+[smhd]|\d{1,2}h)/.test(line),
          ) || "";

        return {
          key: statusLink || text.slice(0, 120),
          statusLink,
          author: lines[0] || "",
          handle,
          time,
          text: text.slice(0, 3000),
          lines: lines.slice(0, 60),
          links: Array.from(new Set(links)).slice(0, 15),
        };
      })
      .filter((item) => item.text && item.statusLink);
  });

  for (const item of items) {
    if (!collected.has(item.key)) {
      collected.set(item.key, item);
    }
  }

  const batchLinks = items.map((item) => item.statusLink).filter(Boolean);
  const hasUsefulBatch = batchLinks.length >= 6;
  const knownMatches = batchLinks.filter((link) => knownLinks.has(link)).length;
  const hitKnownBatch = hasUsefulBatch && knownMatches / batchLinks.length >= 0.85;

  if (hitKnownBatch) {
    knownBatchCount += 1;
  } else {
    knownBatchCount = 0;
  }

  if (collected.size === lastSize) {
    sameCount += 1;
  } else {
    sameCount = 0;
  }
  lastSize = collected.size;

  const now = Date.now();
  if (step === 0 || now - lastProgressAt >= 5000) {
    lastProgressAt = now;
    logProgress(step, batchLinks.length, knownMatches);
  }

  if (sameCount >= 8) {
    stopReason = "stagnant";
    logProgress(step, batchLinks.length, knownMatches, "Reached repeated stagnant viewport threshold");
    break;
  }

  if (knownLinks.size > 0 && knownBatchCount >= 3) {
    stopReason = "known-links";
    logProgress(step, batchLinks.length, knownMatches, "Reached known bookmark area; stopping incremental export early");
    break;
  }

  await page.evaluate(() => window.scrollBy(0, window.innerHeight * 1.3));
  await page.waitForTimeout(2200);
}

const items = Array.from(collected.values());
const savedPath = await writeFile("x-bookmarks-to-obsidian-export.json", JSON.stringify(items, null, 2));

console.log(
  JSON.stringify(
    {
      count: items.length,
      savedPath,
      stopReason,
      knownLinks: knownLinks.size,
    },
    null,
    2,
  ),
);
