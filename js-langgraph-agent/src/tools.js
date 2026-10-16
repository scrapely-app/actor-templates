import { DynamicStructuredTool } from '@langchain/core/tools';
import { load } from 'cheerio';
import { log } from 'scrapely';
import { z } from 'zod';

const BLOCK_ELEMENTS =
    'a, address, article, aside, blockquote, br, button, dd, div, dt, h1, h2, h3, h4, h5, h6, hr, li, main, p, pre, section, td, th, tr';

const DEFAULT_MAX_CHARS = 8000;

/**
 * Tool for browsing the web.
 * Fetches a web page and returns its title and cleaned-up text content.
 */
export const webBrowserTool = new DynamicStructuredTool({
    name: 'browse_web_page',
    description: 'Fetch a web page by its URL and return its title and text content',
    schema: z.object({
        url: z.string().url().describe('Absolute URL of the web page to fetch, e.g. https://crawlee.dev'),
        maxChars: z
            .number()
            .int()
            .positive()
            .default(DEFAULT_MAX_CHARS)
            .describe('The maximum number of characters of page text to return'),
    }),
    func: async ({ url, maxChars }) => {
        log.info(`Fetching web page: ${url}`);

        const response = await fetch(url, {
            headers: { 'User-Agent': 'Mozilla/5.0 (compatible; ScrapelyActor/1.0)' },
            signal: AbortSignal.timeout(30_000),
        });

        if (!response.ok) {
            throw new Error(`Failed to fetch ${url}: ${response.status} ${response.statusText}`);
        }

        const $ = load(await response.text());
        const title = $('title').text().trim();
        $('script, style, noscript, svg, iframe').remove();
        // Separate text of block elements and links with spaces so that words don't get glued together.
        $(BLOCK_ELEMENTS).after(' ');
        const text = $('body').text().replace(/\s+/g, ' ').trim().slice(0, maxChars);

        return `### ${title || url}\nURL: ${response.url}\n\n${text}`;
    },
});
