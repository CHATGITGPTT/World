import os

# Create backend folder structure
os.makedirs('backend', exist_ok=True)

# package.json content
package_json = '''{
  "name": "webscraper-backend",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": {
    "start": "node index.js"
  },
  "dependencies": {
    "playwright": "^1.36.0",
    "express": "^4.18.2",
    "body-parser": "^1.20.2",
    "cors": "^2.8.5",
    "robots-txt-parser": "^0.4.1",
    "cheerio": "^1.0.0-rc.12"
  }
}'''

# index.js content
index_js = '''
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const scraperRouter = require('./scraper');

const app = express();
const port = 3001;

app.use(cors());
app.use(bodyParser.json());

app.use('/api/scrape', scraperRouter);

app.listen(port, () => {
  console.log(`Web scraper backend running on port ${port}`);
});
'''

# scraper.js content
scraper_js = '''
const express = require('express');
const router = express.Router();
const { chromium } = require('playwright');
const cheerio = require('cheerio');
const RobotsParser = require('robots-txt-parser');

const robotsParser = new RobotsParser({
  userAgent: 'AdvancedWebScraperBot',
  allowOnNeutral: true
});

// Helper: delay function
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function fetchRobotsTxt(url) {
  try {
    await robotsParser.setUrl(new URL(url).origin + '/robots.txt');
    await robotsParser.read();
    return true;
  } catch (err) {
    console.warn('Failed to fetch robots.txt:', err);
    return false;
  }
}

async function isAllowed(url) {
  try {
    return await robotsParser.canCrawl(url);
  } catch (err) {
    return true;  // Default allow on error
  }
}

// Core scraping function with crawling, delay, and max depth/pages
async function crawlAndScrape(options) {
  const { startUrl, maxDepth, delayMs, maxPages, respectRobots, followLinks, userAgent } = options;

  const browser = await chromium.launch();
  const context = await browser.newContext({ userAgent });
  const page = await context.newPage();

  const visited = new Set();
  const results = [];
  const queue = [{ url: startUrl, depth: 0 }];

  if (respectRobots) {
    await fetchRobotsTxt(startUrl);
  }

  while (queue.length > 0 && results.length < maxPages) {
    const { url, depth } = queue.shift();

    if (visited.has(url)) continue;
    visited.add(url);

    if (respectRobots && !(await isAllowed(url))) {
      console.log('Disallowed by robots.txt:', url);
      continue;
    }

    if (depth > maxDepth) continue;

    try {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await delay(delayMs);
      const content = await page.content();
      const $ = cheerio.load(content);

      // Basic extraction example: headlines, products, contacts, social links
      // This would be replaced by dynamic selectors based on user intent
      const extracted = [];

      // Articles headlines
      $('h1,h2').each((i, el) => {
        extracted.push({ type: 'headline', text: $(el).text().trim(), url });
      });

      // Price placeholders
      $('.price, [data-price]').each((i, el) => {
        extracted.push({ type: 'price', value: $(el).text().trim(), url });
      });

      // Emails
      $('a[href^="mailto:"]').each((i, el) => {
        extracted.push({ type: 'email', value: $(el).attr('href').replace('mailto:', ''), url });
      });

      // Phones
      $('a[href^="tel:"]').each((i, el) => {
        extracted.push({ type: 'phone', value: $(el).attr('href').replace('tel:', ''), url });
      });

      // Social links
      $('a[href*="twitter.com"], a[href*="facebook.com"], a[href*="instagram.com"]').each((i, el) => {
        extracted.push({ type: 'social_link', url: $(el).attr('href'), platform: $(el).attr('href').match(/(twitter|facebook|instagram).com/)[1] });
      });

      results.push(...extracted);

      if (followLinks && depth < maxDepth) {
        // Add internal links to queue
        $('a[href^="/"]').each((i, el) => {
          const href = $(el).attr('href');
          try {
            let fullUrl = new URL(href, url).toString();
            if (!visited.has(fullUrl)) {
              queue.push({ url: fullUrl, depth: depth + 1 });
            }
          } catch(e) {
            console.warn('Invalid URL skipped:', href);
          }
        });
      }

    } catch (err) {
      console.error('Error scraping:', url, err);
    }
  }

  await browser.close();
  return results.slice(0, maxPages);
}

// POST /api/scrape
router.post('/', async (req, res) => {
  const { url, scrapingRules, userIntent, selectedDataTypes, filters, scrapingMode } = req.body;

  if (!url) {
    return res.status(400).json({ error: 'URL is required' });
  }

  try {
    const userAgent = 'AdvancedWebScraperBot/1.0';
    const data = await crawlAndScrape({
      startUrl: url,
      maxDepth: scrapingRules.maxDepth || 2,
      delayMs: scrapingRules.delay || 1000,
      maxPages: scrapingRules.maxPages || 10,
      respectRobots: scrapingRules.respectRobots ?? true,
      followLinks: scrapingRules.followLinks ?? true,
      userAgent
    });

    // TODO: Implement filter application and data type filtering based on userIntent, selectedDataTypes, filters

    res.json({ scrapedData: data, strategy: 'server-scrape' });
  } catch (err) {
    console.error('Scrape failed:', err);
    res.status(500).json({ error: 'Scraping failed' });
  }
});

module.exports = router;
'''

# Write files
with open('backend/package.json', 'w') as file:
    file.write(package_json)

with open('backend/index.js', 'w') as file:
    file.write(index_js)

with open('backend/scraper.js', 'w') as file:
    file.write(scraper_js)

"Backend files created: package.json, index.js, scraper.js"