import { z } from 'zod';

export const ScrapedPageSchema = z.object({
    url: z.string(),
    title: z.string(),
    text: z.string(),
    textLength: z.number(),
});

export type ScrapedPage = z.infer<typeof ScrapedPageSchema>;
