import { rm } from 'node:fs/promises';

import { CheerioCrawler } from '@crawlee/cheerio';
import { createStuffDocumentsChain } from '@langchain/classic/chains/combine_documents';
import { createRetrievalChain } from '@langchain/classic/chains/retrieval';
import { HNSWLib } from '@langchain/community/vectorstores/hnswlib';
import { Document } from '@langchain/core/documents';
import { ChatPromptTemplate } from '@langchain/core/prompts';
import { ChatOpenAI, OpenAIEmbeddings } from '@langchain/openai';
import { Actor, log } from 'scrapely';

// This is ESM project, and as such, it requires you to specify extensions in your relative imports.
// Read more about this here: https://nodejs.org/docs/latest-v18.x/api/esm.html#mandatory-file-extensions
import { cacheVectorIndex, retrieveVectorIndex } from './vector_index_cache.js';

const BLOCK_ELEMENTS =
    'a, address, article, aside, blockquote, br, button, dd, div, dt, h1, h2, h3, h4, h5, h6, hr, li, main, p, pre, section, td, th, tr';

await Actor.init();

// LLM and embedding calls go through the Scrapely LLM gateway (OpenAI-compatible API, OpenRouter model IDs).
// The run token is used as the API key and token usage is billed to your Scrapely account,
// so no provider API key is needed. If running locally, call `scrapely login` in your terminal first.
const { SCRAPELY_TOKEN } = process.env;
const LLM_BASE_URL = process.env.SCRAPELY_LLM_BASE_URL || 'https://api.scrape.ly/v2/llm/api/v1';

// You can configure the input for the Actor in the Scrapely Console when running on the Scrapely platform or editing
// storage/key_value_stores/default/INPUT.json when running locally.
const {
    startUrls = [{ url: 'https://crawlee.dev/js/docs/introduction' }],
    maxCrawlPages = 3,
    forceRecrawl = false, // Enforce a re-crawl of website content and re-creation of the vector index.
    query = 'What is Crawlee and how do I start using it?',
} = (await Actor.getInput()) || {};

// Local directory where the vector index will be stored.
const VECTOR_INDEX_PATH = './vector_index';

const prompt = ChatPromptTemplate.fromTemplate(
    `Answer the user's question: {input} based on the following context {context}`,
);

if (!SCRAPELY_TOKEN) {
    throw new Error(
        'Please configure the SCRAPELY_TOKEN environment variable! Call `scrapely login` in your terminal to authenticate.',
    );
}

const gatewayOptions = { apiKey: SCRAPELY_TOKEN, configuration: { baseURL: LLM_BASE_URL } };
const embeddings = new OpenAIEmbeddings({ ...gatewayOptions, model: 'openai/text-embedding-3-small' });

// The crawl configuration is also used as the cache key of the vector index.
const crawlConfig = { startUrls, maxCrawlPages };

/**
 * Crawls the start URLs and their sub-pages with CheerioCrawler and returns the page texts as LangChain documents.
 */
async function crawlDocuments() {
    const docs = [];
    // Only sub-pages of the start URLs are crawled, e.g. for `https://example.com/blog`
    // the crawler visits `https://example.com/blog/article-1` but skips `https://example.com/docs`.
    const prefixes = new Set(startUrls.map(({ url }) => url));

    const crawler = new CheerioCrawler({
        maxRequestsPerCrawl: maxCrawlPages,
        async requestHandler({ request, $, enqueueLinks }) {
            // Follow redirects of the start URLs (e.g. `https://example.com` -> `https://www.example.com/`).
            if (request.userData.isStartUrl && request.loadedUrl) prefixes.add(request.loadedUrl);

            // Enqueue the sub-pages before the navigation elements get stripped from the page below.
            await enqueueLinks({
                transformRequestFunction: (req) =>
                    [...prefixes].some((prefix) => req.url.startsWith(prefix)) ? req : false,
            });

            const title = $('title').text().trim();
            $('script, style, noscript, svg, iframe, nav, header, footer').remove();
            // Separate text of block elements and links with spaces so that words don't get glued together.
            $(BLOCK_ELEMENTS).after(' ');
            const text = $('body').text().replace(/\s+/g, ' ').trim();
            log.info(`Crawled ${request.loadedUrl} (${text.length} characters)`);
            if (text) {
                docs.push(new Document({ pageContent: text, metadata: { source: request.loadedUrl, title } }));
            }
        },
    });

    await crawler.run(startUrls.map(({ url }) => ({ url, userData: { isStartUrl: true } })));
    return docs;
}

// This variable will contain a vector index that we will use to retrieve the most relevant documents for a given query.
let vectorStore;

// First, we check if the vector index is already cached. If not, we crawl the website to get the documents.
// By setting up forceRecrawl=true you can enforce a re-crawl of the website content and re-creation of the vector index.
log.info('Fetching cached vector index from key-value store...');
const reinitializeIndex = forceRecrawl || !(await retrieveVectorIndex(crawlConfig));
if (reinitializeIndex) {
    log.info('Vector index was not found.');
    log.info('Crawling the website to gather the data...');
    const docs = await crawlDocuments();
    if (!docs.length) throw new Error('No content was crawled from the start URLs.');

    // Initialize the vector index from the crawled documents.
    log.info(`Feeding vector index with ${docs.length} crawled pages...`);
    vectorStore = await HNSWLib.fromDocuments(docs, embeddings);

    // Save the vector index to the key-value store so that we can skip this phase in the next run.
    log.info('Saving vector index to the disk...');
    await vectorStore.save(VECTOR_INDEX_PATH);
    await cacheVectorIndex(crawlConfig, VECTOR_INDEX_PATH);
}

// Load the vector index from the disk if not already initialized above.
if (!vectorStore) {
    log.info('Initializing the vector store...');
    vectorStore = await HNSWLib.load(VECTOR_INDEX_PATH, embeddings);
}

// Next, create the retrieval chain and enter a query:
const llm = new ChatOpenAI({ ...gatewayOptions, model: 'openai/gpt-4o-mini' });
const combineDocsChain = await createStuffDocumentsChain({
    llm,
    prompt,
});

const chain = await createRetrievalChain({
    combineDocsChain,
    retriever: vectorStore.asRetriever(),
    returnSourceDocuments: true,
});

log.info('Asking model a question...');
const res = await chain.invoke({ input: query });

log.info(`Question: ${query}`);
log.info(`Model response: ${res.answer}`);

// Remove the vector index directory as we have it cached in the key-value store for the next time.
await rm(VECTOR_INDEX_PATH, { recursive: true });

await Actor.setValue('OUTPUT', res);
await Actor.exit();
