# Advanced Web Scraper

A full-stack web scraping application with an intelligent React frontend and Node.js/Playwright backend.

## Features

- 🧠 **Intelligent Intent Analysis** - Automatically detects what you want to extract
- 🎯 **Adaptive Scraping Strategies** - Chooses the best approach based on your intent
- 📊 **Multiple Data Types** - Extract text, images, links, metadata, and structured data
- ⚙️ **Customizable Settings** - Control depth, delays, and behavior
- 📈 **Real-time Progress** - Watch scraping in real-time
- 💾 **Export Options** - JSON and CSV formats
- 🔒 **Ethical Scraping** - Respects robots.txt and rate limits

## Project Structure

```
webScraper/
├── frontend/          # React TypeScript frontend
│   ├── src/
│   │   ├── AdvancedWebScraper.tsx
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── backend/           # Node.js Express backend
│   ├── index.js      # Main server
│   ├── scraper.js    # Scraping logic
│   └── package.json
└── README.md
```

## Quick Start

### 1. Install Dependencies

#### Backend
```bash
cd backend
npm install
npx playwright install chrome
```

#### Frontend
```bash
cd frontend
npm install
```

### 2. Start the Backend
```bash
cd backend
npm start
```
The backend will run on http://localhost:3001

### 3. Start the Frontend
```bash
cd frontend
npm run dev
```
The frontend will run on http://localhost:3000

## Usage

1. **Enter URL**: Input the website you want to scrape
2. **Describe Intent**: Tell the scraper what you want to extract
   - "Get all product prices and reviews"
   - "Extract contact information"
   - "Find all article headlines"
3. **Choose Mode**: Select scraping strategy
4. **Configure Settings**: Adjust depth, delays, and filters
5. **Start Scraping**: Click "Start Scraping" and watch the magic happen!

## Supported Intent Types

- **E-commerce**: Prices, products, reviews
- **News/Content**: Headlines, articles, dates, authors
- **Contact Info**: Emails, phones, addresses
- **Social Media**: Social links, profiles, posts
- **Structured Data**: Tables, lists, organized information

## Backend API

### POST /api/scrape

**Request Body:**
```json
{
  "url": "https://example.com",
  "userIntent": "Get all product prices",
  "scrapingRules": {
    "maxDepth": 2,
    "delay": 1000,
    "maxPages": 10,
    "followLinks": true,
    "respectRobots": true
  },
  "selectedDataTypes": {
    "text": true,
    "images": true,
    "links": true,
    "metadata": true,
    "structured": true
  },
  "filters": {
    "minTextLength": 10,
    "excludeNavigation": true,
    "includeHidden": false
  },
  "scrapingMode": "intelligent",
  "selectors": [".price", ".product-title"]
}
```

**Response:**
```json
{
  "scrapedData": [
    {
      "type": "price",
      "value": "$99.99",
      "url": "https://example.com/product/1"
    }
  ],
  "strategy": "server-scrape"
}
```

## Technologies Used

- **Frontend**: React 18, TypeScript, Tailwind CSS, Vite
- **Backend**: Node.js, Express, Playwright, Cheerio
- **Scraping**: Playwright for browser automation, Cheerio for HTML parsing
- **Styling**: Tailwind CSS for modern UI

## Ethical Scraping

- ✅ Respects robots.txt
- ✅ Configurable delays between requests
- ✅ Rate limiting and concurrency control
- ✅ User-agent identification
- ✅ Follows website terms of service

## Development

### Adding New Data Types

1. Update the `analyzeUserIntent` function in `AdvancedWebScraper.tsx`
2. Add corresponding selectors and extraction logic in `scraper.js`
3. Update the type mapping in the backend filtering logic

### Custom Selectors

The system supports custom CSS selectors based on user intent. These are automatically generated but can be enhanced for specific use cases.

## Troubleshooting

### Common Issues

1. **Playwright Browser Not Found**
   ```bash
   npx playwright install chrome
   ```

2. **CORS Issues**
   - Ensure backend is running on port 3001
   - Check that frontend proxy is configured correctly

3. **Scraping Fails**
   - Check if target website blocks automated requests
   - Verify URL is accessible
   - Check browser console for errors

### Logs

- Backend logs are displayed in the terminal
- Frontend errors are shown in the browser console
- Network requests can be monitored in browser DevTools

## License

This project is for educational and development purposes. Always respect website terms of service and robots.txt when scraping.

