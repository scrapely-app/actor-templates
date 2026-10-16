import { createTool } from '@mastra/core/tools';
import { load } from 'cheerio';
import { log } from 'scrapely';
import { z } from 'zod';

import { ScrapedPageSchema } from './models.js';
import type { ScrapedPage } from './models.js';

const BLOCK_ELEMENTS =
    'a, address, article, aside, blockquote, br, button, dd, div, dt, h1, h2, h3, h4, h5, h6, hr, li, main, p, pre, section, td, th, tr';

const MAX_TEXT_LENGTH = 8000;

const scrapePageInputSchema = z.object({
    url: z.string().describe('Absolute URL of the web page to scrape, e.g. https://crawlee.dev'),
});

// Define the web page scraper tool
export const scrapePageTool = createTool({
    id: 'scrape_page',
    description: 'Fetches a web page by its URL and returns its title and text content.',
    inputSchema: scrapePageInputSchema,
    outputSchema: ScrapedPageSchema,
    execute: async ({ url }): Promise<ScrapedPage> => {
        log.info(`Scraping page: ${url}`);

        const response = await fetch(url, {
            headers: { 'User-Agent': 'Mozilla/5.0 (compatible; ScrapelyActor/1.0)' },
            signal: AbortSignal.timeout(30_000),
        });
        if (!response.ok) {
            throw new Error(`Failed to fetch ${url}: ${response.status} ${response.statusText}`);
        }

        // Strip scripts and styles and keep only the visible text (truncated to keep the LLM context small)
        const $ = load(await response.text());
        const title = $('title').text().trim();
        $('script, style, noscript, svg, iframe').remove();
        // Separate text of block elements and links with spaces so that words don't get glued together.
        $(BLOCK_ELEMENTS).after(' ');
        const text = $('body').text().replace(/\s+/g, ' ').trim();

        return { url: response.url, title, text: text.slice(0, MAX_TEXT_LENGTH), textLength: text.length };
    },
});
