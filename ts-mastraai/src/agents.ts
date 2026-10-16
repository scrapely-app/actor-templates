import { createOpenAI } from '@ai-sdk/openai';
import { Agent } from '@mastra/core/agent';

import { scrapePageTool } from './tools.js';

// LLM calls go through the Scrapely LLM gateway (OpenAI-compatible API, OpenRouter model IDs).
// The run token is used as the API key and token usage is billed to the Scrapely account running the Actor,
// so no provider API key is needed.
const gateway = createOpenAI({
    baseURL: process.env.SCRAPELY_LLM_BASE_URL || 'https://api.scrape.ly/v2/llm/api/v1',
    apiKey: process.env.SCRAPELY_TOKEN,
});

export const createWebResearchAgent = (modelName: string): Agent =>
    new Agent({
        id: 'web-research-agent',
        name: 'Web Research Agent',
        instructions: `You are an expert web researcher. You help users understand websites and topics
        by reading web pages with the scrape_page tool and extracting meaningful insights from their content.
        Always base your answers on the scraped content and cite the URLs you used.`,
        // `.chat()` uses the Chat Completions API (/chat/completions) supported by the gateway
        model: gateway.chat(modelName),
        tools: { scrapePageTool },
    });
