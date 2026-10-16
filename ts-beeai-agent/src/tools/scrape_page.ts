import { Emitter } from 'beeai-framework/emitter/emitter';
import type { AnyToolSchemaLike } from 'beeai-framework/internals/helpers/schema';
import type { ToolEmitter, ToolInput } from 'beeai-framework/tools/base';
import { JSONToolOutput, Tool } from 'beeai-framework/tools/base';
import { load } from 'cheerio';
import { log } from 'scrapely';
import { z } from 'zod';

const BLOCK_ELEMENTS =
    'a, address, article, aside, blockquote, br, button, dd, div, dt, h1, h2, h3, h4, h5, h6, hr, li, main, p, pre, section, td, th, tr';

const MAX_TEXT_LENGTH = 8000;

interface ScrapePageToolOutput {
    url: string;
    title: string;
    text: string;
    textLength: number;
}

/**
 * @class ScrapePageTool
 * @extends Tool
 *
 * @description
 * This class represents a tool for scraping a web page.
 * It fetches the page, strips scripts and styles, and returns the page title
 * and its text content (truncated to keep the LLM context small).
 */
export class ScrapePageTool extends Tool<JSONToolOutput<ScrapePageToolOutput>> {
    override name = 'scrape_page';

    override description = 'Fetches a web page by its URL and returns its title and text content.';

    override inputSchema(): Promise<AnyToolSchemaLike> | AnyToolSchemaLike {
        return z
            .object({
                url: z.string().describe('Absolute URL of the web page to scrape, e.g. https://crawlee.dev'),
            })
            .required({ url: true });
    }

    public readonly emitter: ToolEmitter<ToolInput<this>, JSONToolOutput<ScrapePageToolOutput>> = Emitter.root.child({
        namespace: ['tool', 'scrape_page'],
        creator: this,
    });

    protected async _run(input: ToolInput<this>): Promise<JSONToolOutput<ScrapePageToolOutput>> {
        const { url } = input;
        log.info(`Scraping page: ${url}`);

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
        const text = $('body').text().replace(/\s+/g, ' ').trim();

        return new JSONToolOutput({
            url: response.url,
            title,
            text: text.slice(0, MAX_TEXT_LENGTH),
            textLength: text.length,
        });
    }

    static {
        // Makes the class serializable
        this.register();
    }
}
