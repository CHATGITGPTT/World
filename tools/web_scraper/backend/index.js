
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
