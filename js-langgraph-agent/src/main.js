import { HumanMessage } from '@langchain/core/messages';
import { ChatOpenAI } from '@langchain/openai';
import { createAgent } from 'langchain';
import { Actor, log } from 'scrapely';

import { webBrowserTool } from './tools.js';

await Actor.init();

log.info('Charging Actor start event.');
await Actor.charge({ eventName: 'actor-start' });

// LLM calls go through the Scrapely LLM gateway (OpenAI-compatible API, OpenRouter model IDs).
// The run token is used as the API key and token usage is billed to your Scrapely account,
// so no provider API key is needed. If running locally, call `scrapely login` in your terminal first.
const { SCRAPELY_TOKEN } = process.env;
const LLM_BASE_URL = process.env.SCRAPELY_LLM_BASE_URL || 'https://api.scrape.ly/v2/llm/api/v1';
const { query, modelName = 'openai/gpt-4o' } = (await Actor.getInput()) ?? {};

if (!SCRAPELY_TOKEN) {
    throw new Error(
        'Please configure the SCRAPELY_TOKEN environment variable. Call `scrapely login` in your terminal.',
    );
}

const llm = new ChatOpenAI({
    temperature: 0,
    model: modelName,
    apiKey: SCRAPELY_TOKEN,
    configuration: { baseURL: LLM_BASE_URL },
});

const agent = createAgent({
    model: llm,
    tools: [webBrowserTool],
    systemPrompt:
        'You are a helpful research assistant. When the question refers to a web page or website, ' +
        'use the browse_web_page tool to read it and base your answer on its content. Cite the URLs you used.',
});

log.info('Starting agent...');
const agentFinalState = await agent.invoke(
    { messages: [new HumanMessage(query)] },
    { configurable: { thread_id: '1' } },
);

if (!agentFinalState?.messages?.length) {
    throw new Error('Agent did not return a valid response.');
}

const answer = agentFinalState.messages.at(-1).content;

log.info(`Question: ${query}`);
log.info(`Agent response: ${answer}`);
log.info(`Number of messages: ${agentFinalState.messages.length}`);

log.info('Pushing data to the dataset');
await Actor.pushData({ question: query, answer });

log.info('Charging for task completion');
await Actor.charge({ eventName: 'task-completed' });

await Actor.exit();
