
const express = require('express');
const router = express.Router();
const { chromium } = require('playwright');
const cheerio = require('cheerio');
const robotsParser = require('robots-parser');
const https = require('https');
const http = require('http');

// Helper: delay function
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function fetchRobotsTxt(url) {
  return new Promise((resolve) => {
    try {
      const robotsUrl = new URL(url).origin + '/robots.txt';
      const protocol = robotsUrl.startsWith('https:') ? https : http;
      
      const req = protocol.get(robotsUrl, (res) => {
        let data = '';
        res.on('data', (chunk) => {
          data += chunk;
        });
        res.on('end', () => {
          try {
            const parser = robotsParser(data);
            resolve(parser);
          } catch (err) {
            console.warn('Failed to parse robots.txt:', err);
            resolve(null);
          }
        });
      });
      
      req.on('error', (err) => {
        console.warn('Failed to fetch robots.txt:', err);
        resolve(null);
      });
      
      req.setTimeout(5000, () => {
        console.warn('Timeout fetching robots.txt');
        resolve(null);
      });
    } catch (err) {
      console.warn('Failed to fetch robots.txt:', err);
      resolve(null);
    }
  });
}

async function isAllowed(url, robotsParserInstance) {
  try {
    if (!robotsParserInstance) return true;
    return robotsParserInstance.isAllowed(url, 'AdvancedWebScraperBot');
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

  let robotsParserInstance = null;
  if (respectRobots) {
    robotsParserInstance = await fetchRobotsTxt(startUrl);
  }

  while (queue.length > 0 && results.length < maxPages) {
    const { url, depth } = queue.shift();

    if (visited.has(url)) continue;
    visited.add(url);

    if (respectRobots && !(await isAllowed(url, robotsParserInstance))) {
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
  const { url, scrapingRules, userIntent, selectedDataTypes, filters, scrapingMode, selectors } = req.body;

  if (!url) {
    return res.status(400).json({ error: 'URL is required' });
  }

  try {
    const userAgent = 'AdvancedWebScraperBot/1.0';
    let data = await crawlAndScrape({
      startUrl: url,
      maxDepth: scrapingRules.maxDepth || 2,
      delayMs: scrapingRules.delay || 1000,
      maxPages: scrapingRules.maxPages || 10,
      respectRobots: scrapingRules.respectRobots ?? true,
      followLinks: scrapingRules.followLinks ?? true,
      userAgent
    });

    // Apply data type filtering
    if (selectedDataTypes) {
      data = data.filter(item => {
        // Map item types to selected data types
        const typeMap = {
          'headline': 'text',
          'price': 'structured',
          'email': 'text',
          'phone': 'text',
          'social_link': 'links',
          'product': 'structured',
          'review': 'text',
          'article': 'text',
          'contact': 'text',
          'address': 'text'
        };
        const mappedType = typeMap[item.type] || 'text';
        return selectedDataTypes[mappedType];
      });
    }

    // Apply filters
    if (filters) {
      if (filters.minTextLength) {
        data = data.filter(item => {
          const text = item.text || item.value || '';
          return text.length >= filters.minTextLength;
        });
      }

      if (filters.excludeNavigation) {
        data = data.filter(item => {
          const text = item.text || item.value || '';
          const navKeywords = ['home', 'about', 'contact', 'login', 'signup', 'menu', 'navigation'];
          return !navKeywords.some(keyword => text.toLowerCase().includes(keyword));
        });
      }
    }

    // Apply custom selectors if provided
    if (selectors && selectors.length > 0) {
      // This would require re-scraping with custom selectors
      // For now, we'll enhance existing data
      console.log('Custom selectors provided:', selectors);
    }

    res.json({ scrapedData: data, strategy: 'server-scrape' });
  } catch (err) {
    console.error('Scrape failed:', err);
    res.status(500).json({ error: 'Scraping failed' });
  }
});

module.exports = router;
