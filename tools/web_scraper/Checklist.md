## Frontend ↔ Backend integration checklist

Below is a consolidated list of every gap that still prevents your React UI (`webscraper.tsx`) and the Node/Playwright backend from working end-to-end, followed by the concrete fix for each.

| # | Gap | Effect | Fix (code-level) |
|---|-----|--------|------------------|
| **1** | Frontend still calls `simulateWebScraping()` (mock) | UI shows fake data; backend never called | -  Delete `simulateWebScraping` and `generateMockData`.<br>-  Replace `handleScrape` body with:  ```ts  const res = await fetch('http://localhost:3001/api/scrape', {    method: 'POST',    headers: { 'Content-Type': 'application/json' },    body: JSON.stringify({      url, userIntent, scrapingRules, selectedDataTypes, filters, scrapingMode    })  });  const json = await res.json();  setScrapedData(json.scrapedData);  ```
| **2** | No progress feedback from server | “Scraping…” spinner shows until request ends | -  On backend, stream partial results via Server-Sent Events (SSE) or WebSocket.<br>-  On frontend, listen to the stream and `setScrapedData(prev ⇒ [...prev, …chunk])`. |
| **3** | Back-end ignores `selectedDataTypes` and `filters` | UI toggles have no effect | -  After `const data = await crawlAndScrape…`, insert: ```js  let filtered = data.filter(item ⇒ selectedDataTypes[item.type]);  if (filters.minTextLength)   filtered = filtered.filter(i ⇒ !i.text || i.text.length ≥ filters.minTextLength);  // exclude nav, includeHidden, language etc.  ```
| **4** | Intent-driven selectors not wired to backend | Extraction remains generic | -  In React, keep `analysisResults.selectors` from your intent analysis.<br>-  Send them in the POST body: `selectors: analysisResults.selectors`.<br>-  In `crawlAndScrape`, accept `customSelectors` and run:<br>```js  customSelectors.forEach(sel ⇒ { $(sel).each((_, el) ⇒ results.push({ type: sel, text: $(el).text().trim(), url })); }); ```
| **5** | Playwright binaries may be missing | Backend throws “browser executable not found” | -  Document (or include in Dockerfile) `npx playwright install chrome`.<br>-  Optionally call `require('playwright').install()` on first run. |
| **6** | Front-end hard-codes API host | Breaks when deployed on a different origin | -  Use env variable: `const API_BASE = import.meta.env.VITE_SCRAPER_API || '/api';` |
| **7** | Browser not closed on early throw | Memory leaks | -  Wrap crawl loop in `try { … } finally { await browser.close(); }`. |
| **8** | robots.txt parser re-downloads for each request | Unnecessary latency | -  Cache parser per `origin` inside a Map. |
| **9** | No rate-limiting / concurrency guard | Risk of target-site bans | -  Add `p-queue` in backend to cap concurrent browsers; expose `queue.size` for UI progress. |
| **10** | No CORS headers for deployed frontend | Requests blocked in prod | -  Keep `app.use(cors())`, but when you deploy, pass `{ origin: 'https://your-frontend.com' }`. |
| **11** | Missing error UI | Silent failure if backend 4xx/5xx | -  Wrap `fetch` in `try/catch`; on error `setError(err.message)` and show alert banner. |
| **12** | No pagination of large result sets | UI stalls on thousands of nodes | -  Backend: slice to max 10,000 or implement cursor.<br>-  Frontend: virtualize list (e.g., react-window). |

### Minimal code-patch snippet for React `handleScrape`

```ts
const handleScrape = async () => {
  if (!url.trim()) return;
  setIsLoading(true);
  try {
    const res = await fetch(import.meta.env.VITE_SCRAPER_API ?? 'http://localhost:3001/api/scrape', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url,
        userIntent,
        scrapingRules,
        selectedDataTypes,
        filters,
        scrapingMode,
        selectors: analyzeUserIntent(userIntent, url).selectors // new
      })
    });
    if (!res.ok) throw new Error(await res.text());
    const { scrapedData } = await res.json();
    setScrapedData(scrapedData);
  } catch (e) {
    alert(`Scrape failed: ${e.message}`);
  } finally {
    setIsLoading(false);
  }
};
```

### After these fixes

1. `npm install && npx playwright install chrome && npm start` inside `backend/`.  
2. `npm run dev` for the React app.  
3. Enter a URL and intent → backend crawls with Playwright, applies selectors, returns live data → UI renders real results, export works.

Implementing each numbered fix above will close every functional gap and give you a fully operational, intent-aware web-scraper running with a modern React front-end and a Playwright/Cheerio Node backend.